from databroker import catalog

db = catalog["msgpack-bpm-experiment"]
uid = -1
run = db[uid]
dataX = run.primary.read()
print(f"data came: {dataX}")

print(dataX.bpm_elem_data[2])
