def read_overlaps_csv(csv_url):

    # Read file line by line, splitting by the delimiter
    data = []
    with open(csv_url, 'r') as file:
        for line in file:
            data.append(line.strip().split(','))

    # Convert to DataFrame, padding shorter rows with NaN
    df = pd.DataFrame(data)
    df.columns = df.iloc[0]
    df.drop(index=0, inplace=True)
    
    return df

