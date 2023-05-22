# Scripts for analyzing criminal minds data

## Data collection and processing

The following scripts are using for generating data.

Criminal data can be generated using `./scraping_criminals.py`. 
This file accepts a desired export path as a command line argument and can be run as follows:

```sh
python3 ./scraping_criminals.py --export_path <path>
```

Details on the structure of the exported data can be found in `../data/README.md`.

Episode data can be generated using `./scraping_criminals.py`. 
This file accepts a desired export path as a command line argument and can be run as follows:

```sh
python3 ./scraping_episodes.py --export_path <path>
```


## Data analysis

