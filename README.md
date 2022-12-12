# Auction based real-time traffic signal control

## About the project

This is a course project of CEE 551 (2022Fall). In this project, we use 
an auction based algorithm to control the switch between phases. The weight 
is calibrated offline by the algorithm ... .
The final result is tested in [SUMO](https://www.eclipse.org/sumo/).

## Getting Started

### Prerequisites

#### Python

This project is compatible with Python 3.9+.

#### SUMO

You need to install SUMO to run the simulation, you can find 
instruction [here](https://sumo.dlr.de/docs/Downloads.php#linux_binaries).

#### Virtual Environment

Virtual environment is highly recommended for all the project in mtldp. It can help you
isolate your project environment from one to another. With virtual environment, you can
avoid most dependency issue and reproducible problems.

You can use [Anaconda](https://docs.anaconda.com/anaconda/install/index.html)
or [Miniconda](https://docs.conda.io/en/latest/miniconda.html), or you can use python
standard library `[venv](https://docs.python.org/3.8/library/venv.html)`.

Anaconda/Miniconda will be used in the following documentation.

### Usage

### Get the source code

Get the source code via `git clone` command.

#### Create virtual environment

```shell
$ conda create -n cee-551 python=3.9 -y
$ conda activate cee-551
(cee-551) $
```

#### Install the dependencies
```shell
(cee-551) $ pip install -r requirements.txt
```


#### Run the simulation

You can run the test with following command:

```shell
(cee-551) $ python test_auction_based.py
```

Or

```shell
(cee-551) $ python test_fixed.py
```
