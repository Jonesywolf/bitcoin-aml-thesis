# A Satoshi-Sized Bitcoin Sub-Graph Money Laundering Detection Model
As money digitizes and cryptocurrencies rise in popularity, currencies must replicate the privacy of cash while preventing fraud and money laundering to remain relevant. To maintain this tenuous balance, novel money laundering detection tools must recognize suspicious activity. More effective money laundering detection tools can be devised with the release of the Elliptic2 dataset, containing over 196 million transactions with labelled fraudulent sub-graphs. However, these complex models have longer inference times and require more computing resources. This diminishes their practicality and raises the barrier to entry for those new to the space. In response to this challenge, a new money laundering detection model was developed and characterized using standard metrics on the Elliptic2 dataset on a standard multi-threaded CPU. Sacrificing accuracy for speed and portability, this new model can be run as part of a web application for visualizing the blockchain and democratizing access to anti-money laundering tools. 


## Building
Clone the repository and build the docker images:
```bash
sudo docker build -t ghcr.io/jonesywolf/bitcoin-aml-thesis/api:latest -f ./api/Dockerfile.api ./api
sudo docker build -t ghcr.io/jonesywolf/bitcoin-aml-thesis/worker:latest -f ./web/Dockerfile.worker ./worker
```