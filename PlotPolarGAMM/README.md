# PlotPolarGAMM
PlotPolarGAMM is a function that allows you to visualize and plot Plotly figures of GAMM-fitted ultrasound tongue contours with provided GAMM models.

```
plotPolarGAMM(
model,
targetName,
targetL,
rmax,
view='X',
showLegend=T,
showDiff=T,
fontSize=25,
returnData=F
)
```

### Arguments
#### model
A GAMM model, resulting from the functions gam or bam.
#### target
The name of the categories of different types of sounds (e.g. *vowel* for tokens of /i/, /a/, and /u/, or *place* for alveolar and velar sounds.)
#### targetL
The categories of the target (e.g. use c('i', 'a', 'u') for the *vowel* example previously, or c('velar', 'alvolar') for the *place* example.)
#### rmax
The maximum radius of the plot.
#### view
The predictor, usually 'X'.
#### showLegend
Whether to show the legend.
#### showDiff
Whether to plot the different areas, indicated by gray color blocks.
#### fontSize
The font size.
#### returnData
Whether to return the fitted data as a dataframe. If False, it will return a Plotly plot.
