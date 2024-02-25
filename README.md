# How many of the top 100'000 websites use Cloudflare?

This program uses a dataset of the top 100'000 websites to determine how many of them use Cloudflare.  
Attention: It is highly recommended to not run this program at home,
as it will generate a lot of traffic and your Internet access might stop working for a while.
It is recommended to run this program on a server or a cloud instance.  
This program uses 100 threads to analyze the data.

## Requirements
- Python 3.8 or higher
- No additional packages

## Usage
Just run `python3 main.py`

## Data Attribution

The dataset used in this subproject, "100k.csv", was obtained from Cloudflare Radar and is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

**Attribution:**
- Original Data Source: [Cloudflare Radar](https://radar.cloudflare.com/charts/LargerTopDomainsTable/attachment?id=954&top=100000&startDate=2024-01-22&endDate=2024-01-29)
- Author: [Cloudflare](https://www.cloudflare.com/)


## License
Copyright 2024, DAMcraft
This project is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full license text.
