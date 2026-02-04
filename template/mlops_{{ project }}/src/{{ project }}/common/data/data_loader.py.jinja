from loguru import logger


def data_helper(spark, config):
    source_type = config.get("source_data_type")
    
    flag = False
    if source_type == "databricks_table":
        table_name = config.get("inputs")["databricks_table"]
        df_table = spark.sql(f"SELECT * FROM {table_name}")
        logger.info(f"Table read successfully - `{table_name}`.")
        flag = True
    else:
        message = f"Supports only `databricks_table` as of now."
        logger.error(message)
        raise ValueError(message)
    
    if flag:
        target_info = config.get("outputs")
        target_table = target_info["databricks_table"]
        df_table.write.format("delta").mode("overwrite").saveAsTable(f"{target_table}")
        logger.info(f"Source data written successfully - `{target_table}`")
    
    return True


def load_data(spark, func_conf):
    config = func_conf["kwargs"]
    data_output = data_helper(spark=spark, config=config)
    return data_output