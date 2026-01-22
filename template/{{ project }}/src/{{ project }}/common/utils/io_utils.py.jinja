import os
import shutil
import json
import pandas as pd

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    TimestampType,
)
from pyspark.sql.functions import col
from loguru import logger


def setup_project_output_path(spark, func_conf):
    project_name = func_conf["kwargs"]["project_name"]
    model_name = func_conf["kwargs"]["model_name"]
    volumes_root_path = func_conf["kwargs"].get("volumes_root_path")

    if volumes_root_path:
        folder_name = os.path.join(project_name, f"{model_name}_outputs")
        project_output_path = os.path.join(volumes_root_path, folder_name)

        if os.path.exists(project_output_path):
            logger.warning(
                f"{model_name} project output path already exists. Recreating it after cleaning up."
            )
            shutil.rmtree(project_output_path)
            logger.info(f"Successfully deleted the {project_output_path}.")

        os.makedirs(project_output_path, exist_ok=True)
        logger.success(
            f"Successfully created {model_name} project output path in volumes."
        )

        return True
    
    logger.warning("No volumes path provided.")


def cleanup_pipeline_setup(spark, func_conf):
    project_name = func_conf["kwargs"]["project_name"]
    model_name = func_conf["kwargs"]["model_name"]
    volumes_root_path = func_conf["kwargs"].get("volumes_root_path", None)

    if volumes_root_path:
        folder_name = os.path.join(project_name, f"{model_name}_outputs")
        project_output_path = os.path.join(volumes_root_path, folder_name)

        records = []
        # TODO:
        # 1. Add more output stages - files to process
        files_to_process = ["data_extraction.json", "data_featurization.json"]
        for file in files_to_process:
            file_path = os.path.join(project_output_path, file)
            if os.path.exists(file_path):
                with open(file=file_path, mode="r") as fp:
                    metrics_data = json.load(fp=fp)
                    records.append(metrics_data)
                    logger.info(f"Successfully read the file `{file_path}`.")

        audit_schema = StructType(
            [
                StructField("project_name", StringType(), True),
                StructField("model_name", StringType(), True),
                StructField("stage_name", StringType(), True),
                StructField("task_name", StringType(), True),
                StructField("task_run_id", StringType(), True),
                StructField("job_name", StringType(), True),
                StructField("job_id", StringType(), True),
                StructField("job_run_id", StringType(), True),
                StructField("run_status", StringType(), True),
                StructField("start_time", StringType(), True),
                StructField("end_time", StringType(), True),
                StructField("duration_mins", StringType(), True),
                StructField("error_details", StringType(), True),
            ]
        )

        if records:
            df = spark.createDataFrame(data=records, schema=audit_schema)
            df = df.orderBy(col("start_time"), col("task_name"))
            full_table_name = func_conf["kwargs"]["audit_table"]
            df.write.mode("append").saveAsTable(full_table_name)
            logger.success(f"Audit table created successfully - `{full_table_name}`")
        else:
            logger.warning(
                f"No files found in the project output folder - `{project_output_path}`"
            )

        try:
            shutil.rmtree(project_output_path)
            logger.info(f"Cleaned-up the project output folder - `{project_output_path}`")
        except:
            pass

        return True
    
    logger.warning("No volumes path provided.")
