# maxquant_wrapper

## motivation
* easy high throughput processing 
* the wrapper takes care for the data staging

## input and output



## install

### on Max Quant Server

setup ssh tunnel between host where `fgcz_maxquant_rpc_client.py` runs and where `fgcz_maxquant_rpc_server.py` runs

```bash
$ ssh $USER@fgcz-c-071 -R8084:localhost:8084 -N -v
```

run `fgcz_maxquant_rpc_server.py` with default options

```dos

c:\Python27\python.exe fgcz_maxquant_rpc_server.py
```

