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


def is_table_exists(spark, table_name):
    try:
        spark.table(table_name)
        return True
    except Exception as e:
        return False


def setup_project_audit_table(spark, func_conf):
    project_name = func_conf["kwargs"]["project_name"]
    model_name = func_conf["kwargs"]["model_name"]
    audit_table_name = func_conf["kwargs"].get(
        "audit_table", f"hive_metastore.default.mlops_{project_name}_{model_name}_audit_tbl"
    )
    if audit_table_name.startswith("."):
        logger.warning("`AUDIT_TARGET_CATALOG` is not specified in `config.toml`.")
        logger.info("Cretaing the audit table in `hive_metastore`.")
        audit_table_name = f"hive_metastore.default.mlops_{project_name}_{model_name}_audit_tbl"

    audit_schema = StructType(
        [
            StructField("project_name", StringType(), True),
            StructField("model_name", StringType(), True),
            StructField("stage_name", StringType(), True),
            StructField("task_name", StringType(), True),
            StructField("process_name", StringType(), True),
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

    if is_table_exists(spark, audit_table_name):
        logger.info(f"Table '{audit_table_name}' already exists. Skipping creation.")
    else:
        logger.info(f"Table '{audit_table_name}' does not exist. Creating table.")
        audit_df = spark.createDataFrame([], audit_schema)
        audit_df.write.format("delta").mode("overwrite").saveAsTable(f"{audit_table_name}")

    return True


def write_to_audit_table(spark, audit_metrics, func_conf, audit_table=None):
    project_name = func_conf["kwargs"]["project_name"]
    model_name = func_conf["kwargs"]["model_name"]
    if not audit_table:
        logger.warning("`AUDIT_TARGET_CATALOG` is not specified in `config.toml`.")
        logger.info("Saving the audit details in `hive_metastore`.")
        audit_table = f"hive_metastore.default.mlops_{project_name}_{model_name}_audit_tbl"

    records = [audit_metrics]

    audit_schema = StructType(
        [
            StructField("project_name", StringType(), True),
            StructField("model_name", StringType(), True),
            StructField("stage_name", StringType(), True),
            StructField("task_name", StringType(), True),
            StructField("process_name", StringType(), True),
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
        df.write.mode("append").saveAsTable(audit_table)
        logger.info(f"Audit metrics appended successfully - `{audit_table}`.")
    else:
        logger.warning(
            f"No metrics found to append."
        )

    return True
