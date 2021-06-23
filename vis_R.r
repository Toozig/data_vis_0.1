rm(list=ls())
setwd("C:/Users/Ido/Desktop/Sonification/Visualization")
library(ggplot2)
library(ggpubr)
library(jpeg)
library(dplyr)
library(png)
library(ggimage)
library(RANN)
library(spotifyr)
library(devtools)
library(spotifyr)
Sys.setenv(SPOTIFY_CLIENT_ID = '4cc0d73dc6ae4e64b7318da7236f7f04')
Sys.setenv(SPOTIFY_CLIENT_SECRET = '3a88b3d055854dcb9cfe1a1ed8784942')
Sys.setenv(SPOTIFY_REDIRECT_URI= "http://localhost//")
access_token <- get_spotify_access_token()
df <- gg(include_meta_info = TRUE)
offset <- 1
fav <- df
while(dim(fav) != 0){
  fav <- get_my_top_artists_or_tracks(type = 'tracks', limit = 50, offset = offset)
  df <- rbind(df, fav)
  offset <- offset + 10
  
  
}
func <- function(x){
  return(my_(type="tracks", offset =x, limit = 10))
}

r <-get_my_saved_tracks()
g <- func(50)
h <- func(40)
e <- func(10)
l <-distinct (rbind(g,r))

tail(r$name)
f['preview_url']














func <- function(x){
  # sPath = "C:\\Users\\Ido\\Desktop\\Sonification\\Visualization\\tmpv\\"
  result <- paste0("tmpv\\",x)
  result <- paste0(result, ".jpeg")
  return(result)
}
dg <- read_xlsx("Book2.xlsx", col_names = TRUE)



df <- read.csv('tsne_res.csv', header = TRUE,  encoding="UTF-8")

head(as.matrix(df))


nn2(select(df,c(X0,X1)), cbind(-3,5), 1) %>% sapply(head)


#df$labels <- as.factor(df$labels)
df$img =lapply(df$id, func)
df <- as.data.frame(lapply(df, unlist))
head(df)

plot <- ggplot(df2, aes(x=X0, y=X1,image=img)) +
         geom_point()  +
         geom_image(size=0.02) +
         theme(legend.position = "none",
              axis.title = element_blank(),
              axis.text.x = element_blank(),
              axis.text.y = element_blank(),
              axis.ticks = element_blank())  
ggsave("my_plot.pdf", plot)        


imgDisp <- function(e){
    idx <- nn2(df[, 3:4], cbind(e$x,e$y), 1) %>% sapply(head)
    idx <- idx[1]
    list(src=df[idx, "img"], alt=df[idx,'idx'])
}
idx <- nn2(df[, 3:4],cbind(-5.9,-11.4), 1) %>% 
  sapply(head)



dim(head(df[,3:4]))

closest <- nn2(df[, 3:4], cbind(-5.9,-11.4), 1) %>% sapply(head)
df[closest, "img"]
list(src=df[closest, "img"], alt=df[closest,'index'])
head(df)
