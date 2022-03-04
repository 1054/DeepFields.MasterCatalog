#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, re
import click
import pandas as pd
import pandasgui
from astropy.table import Table




@click.command()
@click.argument('input_fits_file', type=click.Path(exists=True))
def main(input_fits_file):
    print('Reading {input_fits_file!r}')
    tb = Table.read(input_fits_file)
    df = tb.to_pandas()
    pandasgui.show(df)



if __name__ == '__main__':
    main()


