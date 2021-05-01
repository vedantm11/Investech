
base_dir = "dbfs:/mnt/esg/financial_report_data"

def make_files(base_dir, start_date, end_date):


    org_types = f"Russell_top_{Fields.n_orgs}"
    org_dir = os.path.join(base_dir, f"GDELT_data_{org_types}")
    date_string = f"{start_date}__to__{end_date}"
    date_dir = os.path.join(org_dir, date_string)
    dbutils.fs.mkdirs(org_dir)

    exists = False
    subdirs = [x.name for x in dbutils.fs.ls(org_dir)]
    if date_string + "/" in subdirs:
        subsubdirs = [x.name for x in dbutils.fs.ls(date_dir)]
        if "data_as_delta/" in subsubdirs:
            exists = True
    if exists:
        print("Data already created!")
    else:
        print("Creating Data")
        _ = create_and_save_data(start_date, end_date, save_csv=True)


    if exists and "esg_data/" in subsubdirs:
        print("\n\nESG data already created!")
    else:
        print("\n\nMaking Tables")
        make_tables(start_date, end_date)

    print("\n\nComputing Embeddings & Connections")
    make_embeddings_and_connections(start_date, end_date)



start_date = "2020-12-01"
end_date = "2020-12-02"
make_files(base_dir, start_date, end_date)

start_date = "2020-12-01"
end_date = "2020-12-10"
make_files(base_dir, start_date, end_date)

start_date = "2020-11-11"
end_date = "2020-12-12"
make_files(base_dir, start_date, end_date)

start_date = "2020-06-12"
end_date = "2020-12-12"
make_files(base_dir, start_date, end_date)

