# B2G-summary-plots
Repository that stores the scrips and data to produce the EXO-styled (thanks EXO conveners!) summary plots for the B2G PAG of the CMS experiment.


# Procedure to update the plots
The script reads a `.csv` file that could be either manually edited or exported from a Google Sheet. The latter option is of course preferred to avoid overwriting previous changes. The link to the Google Sheet is:

`https://docs.google.com/spreadsheets/d/1uLXOumhcWryveNN7YNJaCkjtkfYACGeRsT4_y8QQXiE/edit?usp=sharing`

Once the `.csv` file (the default name is `B2GBarchartInputTable - ALL.csv`) is up-to-date, run the script with the command:

`python makeEXOBarPlot.py -l -g ALL -b`

where the `-b` option forces the script in the bash mode, `-l` sets the x log scale, and the `-g` option specifies the group of analyses to be plotted. Possible examples are:

 - *ALL*: all B2G groups (default)
 - *DIB*
 - *RES*
 - *VHF*
