rm(list=ls())
setwd("C:/Users/Ido/Desktop/Sonification/Visualization")
library(shiny)
library(ggplot2)
library(ggpubr)
library(jpeg)
library(dplyr)
library(png)
library(ggimage)
library(RANN)
library(readr)
library(igraph)
library(spotifyr)
library(sound)
locale("he")
library(reticulate)
Sys.setlocale("LC_ALL", "Hebrew")
Sys.setenv(SPOTIFY_CLIENT_ID = '4cc0d73dc6ae4e64b7318da7236f7f04')
Sys.setenv(SPOTIFY_CLIENT_SECRET = '3a88b3d055854dcb9cfe1a1ed8784942')
Sys.setenv(SPOTIFY_REDIRECT_URI= "http://localhost/")
setWavPlayer("C:\\Users\\Ido\\Desktop\\Sonification\\Visualization\\wv_player.exe")
access_token <- get_spotify_access_token()


func <- function(x){
  sPath = "C:\\Users\\Ido\\Desktop\\Sonification\\Visualization\\tmpv\\"
  result <- paste0(sPath,x)
  result <- paste0(result, ".jpeg")
  return(result)
}



df <- read.csv('tsne_res.csv', header = TRUE, encoding = "UTF-8")
df$img =lapply(df$id, func)
df$labels <- as.factor(df$labels)
df <- as.data.frame(lapply(df, unlist))
head(df)


ui <- basicPage(
  plotOutput("plot1",
             click = "plot_click",
             dblclick = "plot_dblclick",
             hover = "plot_hover",
             brush = "plot_brush",
              width='100%', height="500"),
  fluidRow(
           column(width = 1,imageOutput(outputId = "curS")),
           column(width = 3,verbatimTextOutput(outputId = "info_click")),
           column(width = 1,imageOutput(outputId = "curH")),
           column(width = 3,verbatimTextOutput(outputId = "info_hover")),
           column(width = 3,actionButton(inputId = "button", label = "create Playlist")))
  )


server <- function(input, output) {
  # zoomable plot 
  ranges <- reactiveValues(x = NULL, y = NULL)
  
  output$plot1 <- renderPlot({
    ggplot(df, aes(x=X0, y=X1,color=labels)) +
      geom_point(size=5)  +
      #geom_image(size=0.02) +
      coord_cartesian(xlim = ranges$x, ylim = ranges$y, expand = TRUE) +
      
      theme(legend.position = "none",
            axis.title = element_blank(),
            axis.text.x = element_blank(),
            axis.text.y = element_blank(),
            axis.ticks = element_blank())  
  })
  
  # When a double-click happens, check if there's a brush on the plot.
  # If so, zoom to the brush bounds; if not, reset the zoom.
  observeEvent(input$plot_dblclick, {
    brush <- input$plot_brush
    if (!is.null(brush)) {
      ranges$x <- c(brush$xmin, brush$xmax)
      ranges$y <- c(brush$ymin, brush$ymax)
      
    } else {
      ranges$x <- NULL
      ranges$y <- NULL
    }
  })
  
  #__________end of zoom code________________________
  
  # information panel #
  nearst_point_idx <- function(x,y){
    idx <- nn2(select(df,c(X0,X1)), cbind(x,y), 1) %>% sapply(head)
    return(idx[1])
  }
  
  
  # small click image
  imgDisp <- function(e){
    if(is.null(e)) return("")
    idx <- nearst_point_idx(e$x,e$y)
    list(src=df[idx,'img'],
         alt=df[idx,'index'],
         width =100,
         height = 95)
  }
 
  
  
  # text of singer and song
  artist_song <- function(e) {
    if(is.null(e)) return("")
    idx <- nearst_point_idx(e$x,e$y)
    split_sa <- strsplit(df[idx,'index'], split = '-')
    paste0("artist: ",split_sa[[1]][2],"\n","song: ", split_sa[[1]][1])
  }
  
  
  output$info_click <- renderText({
    paste0(artist_song(input$plot_click))
  })
  
  output$info_hover <- renderText(({
    paste0(artist_song(input$plot_hover))
  }))
  output$curS <- renderImage({
    imgDisp(input$plot_click)
  }, deleteFile = FALSE)
  
  output$curH <- renderImage({
    imgDisp(input$plot_hover)
  }, deleteFile = FALSE)
  
  #______________ end of information panel _________________
  
  songs_in_area <- function(e){

    filtered <- filter(df, X0 < e$xmax & X0 > e$xmin &
                      X1 < e$ymax & X1 > e$ymin )
    cur_idx <- nn2(select(filtered,c(X0,X1)), cbind(input$plot_click$x,input$plot_click$y), 1) %>% sapply(head)
    cur_row <- filtered[cur_idx[1],]
    i <- 0
    browser()
    while(dim(filtered)[1] != 0 | i < 6){
      filtered <- filtered[-c(cur_idx),]
      url <-  get_track(cur_row['id'])['preview_url']
      if(url == "NULL") {
        if(dim(filtered)[1] > 1){
        cur_idx <- nn2(select(filtered,c(X0,X1)), cbind(cur_row$X0,cur_row$X1), 1) %>% sapply(head)
        cur_row <- filtered[cur_idx[1],]
        }else{
          break
        }
        next
      }
      download.file(url[[1]][1],paste0("tmp_p\\",i,".mp3"), mode='wb')
      if(dim(filtered)[1] > 1){
        cur_idx <- nn2(select(filtered,c(X0,X1)), cbind(cur_row$X0,cur_row$X1), 1) %>% sapply(head)
        cur_row <- filtered[cur_idx[1],]
        i <- i + 1
      } else{
        break
      }
    }
   
    system("python C:\\Users\\Ido\\Desktop\\Sonification\\Visualization\\play_audio.py")
    play("C:\\Users\\Ido\\Desktop\\Sonification\\Visualization\\tmp_p\\all.wav",stay=FALSE, command=WavPlayer())
    
  }
  observeEvent(input$button, {

    if (is.null(input$plot_brush)) return("")
    songs_in_area(input$plot_brush)
    
  })
  
  
}

shinyApp(ui, server)