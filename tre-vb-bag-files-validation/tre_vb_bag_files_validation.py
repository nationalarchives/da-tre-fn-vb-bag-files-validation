#!/usr/bin/env python3
import logging
import os
from s3_lib import checksum_lib
from s3_lib import tar_lib
from s3_lib import object_lib
from s3_lib import common_lib
from datetime import datetime


# Set global logging options; AWS environment may override this though
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Instantiate logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Get environment variable values
env_producer = common_lib.get_env_var(
    'TRE_SYSTEM_NAME', must_exist=True, must_have_value=True)
env_lambda_function_name = common_lib.get_env_var(
    'TRE_LAMBDA_FUNCTION_NAME', must_exist=True, must_have_value=True)
env_environment = common_lib.get_env_var(
    'TRE_ENVIRONMENT', must_exist=True, must_have_value=True)
env_working_bucket = common_lib.get_env_var(
    'TRE_S3_BUCKET', must_exist=True, must_have_value=True)


# input msg has these in the parameters block
KEY_REFERENCE = 'reference'
KEY_S3_BUCKET = 's3Bucket'
KEY_S3_KEY = 's3Key'
KEY_ERRORS = 'errors'
KEY_S3_OBJECT_ROOT = 's3-object-root'
KEY_VALIDATED_FILES = 'validated-files'


def handler(event, context):
    """
    Given tar at input fields `s3Bucket` and `s3Key` in `event`:

    * untar to s3://`env_working_bucket`/`reference`/`executionId' (untar adds aslo the existing root folder of reference)
    * verify checksums of extracted tar's root files using file tagmanifest-sha256.txt
    * verify checksums of extracted tar's data directory files using file manifest-sha256.txt
    * verify the number of extracted files matches the numbers in the 2 manifest files
    """
    logger.info('handler start"')
    logger.info('type(event)="%s', type(event))
    logger.info('event="%s"', event)

    # Get required values from input event's parameters block
    input_params = event['parameters']
    consignment_reference = input_params[KEY_REFERENCE]
    s3_bucket = input_params[KEY_S3_BUCKET]
    s3_key = input_params[KEY_S3_KEY]
    execution_uuid = event['properties']['executionId']

    try:

        # Unpack tar in working bucket
        working_folder_prefix = consignment_reference + '/' + execution_uuid + '/'
        logger.info('working_folder_prefix=%s', working_folder_prefix)
        extracted_object_list = tar_lib.untar_s3_object(
            s3_bucket, s3_key, output_prefix=working_folder_prefix, output_bucket_name=env_working_bucket)
        logger.info('extracted_object_list=%s', extracted_object_list)
        working_folder = working_folder_prefix + consignment_reference
        logger.info('working_folder=%s', working_folder)
        # Verify extracted tar content checksums
        checksum_ok_list = checksum_lib.verify_s3_manifest_checksums(
            env_working_bucket, working_folder)
        logger.info('checksum_ok_list=%s', checksum_ok_list)


        # Determine expected file counts (from manifest files)
        # not main manifest itself
        manifest_root_count = len(checksum_ok_list['root'])
        manifest_data_count = len(checksum_ok_list['data'])
        # +1 file here as root manifest doesn't include itself (Catch-22...)
        manifests_total_count = 1 + manifest_root_count + manifest_data_count

        # Determine how many files were extracted from the archive
        extracted_total_count = len(extracted_object_list)

        # Determine how many of the extracted files are in the data sub-directory
        data_dir = f'{working_folder}/data/'
        data_dir_files = [
            i for i in extracted_object_list if i.startswith(data_dir)]
        extracted_data_count = len(data_dir_files)

        logger.info(
            'manifest_root_count=%s manifest_data_count=%s '
            'manifests_total_count=%s extracted_total_count=%s '
            'extracted_data_count=%s data_dir_files=%s',
            manifest_root_count, manifest_data_count, manifests_total_count,
            extracted_total_count, extracted_data_count, data_dir_files)

        # Confirm untar output file count matches combined manifests' file count
        if extracted_total_count != manifests_total_count:
            raise ValueError(
                f'Incorrect total file count; {manifests_total_count} in '
                f'manifest, but {extracted_total_count} found')

        # Confirm correct number of files in extracted data sub-directory
        if manifest_data_count != extracted_data_count:
            raise ValueError(
                f'Incorrect data file count; {manifest_data_count} in manifest'
                f'but {extracted_data_count} found')

        # Verify there are no additional unexpected files in the s3 location
        s3_check_list = object_lib.s3_ls(s3_bucket, working_folder)
        s3_check_list_count = len(s3_check_list)
        logger.info('s3_check_list_count=%s s3_check_dir=%s',
                    s3_check_list_count, working_folder)
        if s3_check_list_count != extracted_total_count:
            raise ValueError(
                f'Incorrect data file count; {extracted_total_count} extracted'
                f'but {s3_check_list_count} found')

        event_output_ok = {
            "properties": {
                "messageType": "uk.gov.nationalarchives.tre.messages.bag.validate.BagValidate",
                "timestamp": datetime.now().isoformat() + 'Z',
                "function": env_lambda_function_name,
                "producer": "TRE",
                "executionId": event['properties']['executionId'],
                "parentExecutionId": event['properties']['parentExecutionId']
            },
            "parameters": {
                "reference": consignment_reference,
                "consignmentType" : "COURT_DOCUMENT",
                "s3Bucket": s3_bucket,
                "s3ObjectRoot": working_folder
            }
        }
        event_output_ok['parameters']['originator'] = 'mark'

        logger.info(f'event_output_ok:\n%s\n', event_output_ok)
        return event_output_ok
    except ValueError as e:
        logging.error('handler error: %s', str(e))
        event_output_error = {
            "properties": {
                "messageType": "uk.gov.nationalarchives.tre.messages.treerror.TreError",
                "timestamp": datetime.now().isoformat() + 'Z',
                "function": env_lambda_function_name,
                "producer": "TRE",
                "executionId": event['properties']['executionId'],
                "parentExecutionId": event['properties']['parentExecutionId']
            },
            "parameters": {
                KEY_REFERENCE: consignment_reference,
                KEY_ERRORS: [str(e)]
            }
        }

        logger.info(f'event_output_error:\n%s\n', event_output_error)
        return event_output_error
