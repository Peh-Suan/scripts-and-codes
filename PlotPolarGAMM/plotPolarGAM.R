plotPolarGAM <- function(model, targetName, targetL, rmax, view='X', showLegend=T, showDiff=T, fontSize=25, returnData=F){
  require(gss)
  require(ggplot2)
  require(rticulate)
  require(plotly)
  require(itsadug)
  require(sets)
  require(RColorBrewer)
  diffGAM <- function(compared){
    diffDf <- compared
    diffL <- c()
    for(i in 1:length(diffDf$CI)){
      if((diffDf$est[i]+diffDf$CI[i])*(diffDf$est[i]-diffDf$CI[i])>=0){
        diffL <- append(diffL, TRUE)
      }
      else{
        diffL <- append(diffL, FALSE)
      }
    }
    diffPointL <- c()
    diff <- FALSE
    for(i in 1:length(diffL)){
      if(diff != diffL[[i]]){
        diff <- diffL[i]
        diffPointL <- append(diffPointL, diffDf$X[i])
      }
    }
    if(diffL[length(diffL)] == TRUE){
      diffPointL <- append(diffPointL, diffDf$X[length(diffL)])
    }
    return(diffPointL)
  }
  
  colorL <- brewer.pal(8, 'Dark2')
  colorL <- append(colorL, brewer.pal(12, 'Paired'))
  changeName <- function(L, nameL){
    names(L) <-  nameL
    return(L)
  }
  color2rgb <- function(x){
    c <- col2rgb(x)
    return(paste('rgb(', as.character(c[1]), ',', as.character(c[2]),',' , as.character(c[3]), ')', sep = ''))
  }
  plotL <- c()
  for(i in 1:length(targetL)){
    plotL[i] <- plot_smooth(model, view = view, cond = changeName(list(c(targetL[i])), targetName), rug=F, main=as.character(i))
  }
  
  p <- plot_ly(type="scatterpolar", mode="lines")
  for(i in 1:length(targetL)){
    #c1 <- color2rgb(paste(colorL[i], '1', sep=''))
    #c2 <- color2rgb(paste(colorL[i], '2', sep=''))
    c1 <- color2rgb(colorL[i])
    c2 <- color2rgb(colorL[i])
    p <- add_trace(p, theta=plotL[[i]]$X*180/pi, r=plotL[[i]]$fit, line=list(color=c1, width=1.5), name = targetL[i], legendgroup = targetL[i], showlegend=TRUE)
    p <- add_trace(p, theta=plotL[[i]]$X*180/pi, r=plotL[[i]]$ul, line=list(color=c2, dash="dot", width=0.5), name = targetL[i], legendgroup = targetL[i], showlegend=FALSE)
    p <- add_trace(p, theta=plotL[[i]]$X*180/pi, r=plotL[[i]]$ll, line=list(color=c2, dash="dot", width=0.5), name = targetL[i], legendgroup = targetL[i], showlegend=FALSE)
  }
  targetComL <- expand.grid(targetL, targetL)
  targetComS <- c()
  count <- 1
  for(i in 1:length(targetComL[[1]])){
    if(as.character(targetComL[[1]][i]) != as.character(targetComL[[2]][i])){
      targetComS[[count]] <- c(as.character(targetComL[[1]][i]), as.character(targetComL[[2]][i]))
      count <- count + 1
    }
  }
  
  for(i in 1:length(targetComS)){
    targetComS[[i]] <- as.set(targetComS[[i]])
  }
  targetComS <- unique(targetComS)
  
  clr = rgb(0, 0, 0, max=255, alpha=10)
  nonDiff <- c()
  if(showDiff){
    for(com in 1:length(targetComS)){
      showlegend <- showLegend
      diff <- diffGAM(plot_diff(model, view=view, comp=changeName(list(c(strsplit(as.character(targetComS[[com]]), ' ')[[1]], strsplit(as.character(targetComS[[com]]), ' ')[[2]])), targetName)))
      if(length(diff) != 0){
        for(i in c(1:(length(diff)/2))){
          if(length(diff)>2){
            p=add_trace(
              p,
              theta=c(0, seq(diff[1+(i-1)*2]*180/pi, diff[2+(i-1)*2]*180/pi, length.out=30), 0),
              r=c(0, rep(rmax, 30), 0),
              line=list(color="gray", width=0.1),
              fill="toself",
              fillcolor=clr,
              labels = as.character(com),
              showlegend=showlegend,
              name = paste(strsplit(as.character(targetComS[[com]]), ' ')[[1]], 'v.',
                           strsplit(as.character(targetComS[[com]]), ' ')[[2]]),
              legendgroup = paste(strsplit(as.character(targetComS[[com]]), ' ')[[1]], 'v.',
                                  strsplit(as.character(targetComS[[com]]), ' ')[[2]]))
          }else{
            p=add_trace(p, theta=c(0, seq(diff[1]*180/pi, diff[2]*180/pi, length.out=30), 0), r=c(0, rep(rmax, 30), 0), line=list(color="gray", width=0.1), fill="toself", fillcolor=clr, showlegend=showlegend, name = paste(strsplit(as.character(targetComS[[com]]), ' ')[[1]], 'v.', strsplit(as.character(targetComS[[com]]), ' ')[[2]]), legendgroup = paste(strsplit(as.character(targetComS[[com]]), ' ')[[1]], 'v.', strsplit(as.character(targetComS[[com]]), ' ')[[2]]))
          }
          showlegend <- FALSE
        }
      }else{
        nonDiff <- append(nonDiff, paste(strsplit(as.character(targetComS[[com]]), ' ')[[1]], 'v.',
                                         strsplit(as.character(targetComS[[com]]), ' ')[[2]]))
      }
    }
  }
  if(returnData){
    return(plotL)
  }else{
    return(layout(p, polar=list(sector=c(30,145),radialaxis=list(angle=20, range=c(0, 400)),angularaxis=list(thetaunit="degrees",direction="clockwise", rotation=170)),legend=list(orientation="v",xanchor="left", y=0, font=list(size=fontSize)), showlegend=T))
  }
}