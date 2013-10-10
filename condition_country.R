library(ggplot2)
library(reshape2)
library(maps)

d <- read.csv('condition_country.csv', header=TRUE, as.is=TRUE)
d$cname[d$cname == 'United Kingdom'] <- 'UK'
d$cname[d$cname == 'United States'] <- 'USA'
names(d)[3] <- 'region'

## bin the counts
d$count <- cut(d$count, breaks=c(0, 5, 10, 20, 30, 60))
by(d, d$year, function(rows) {
  world <- map_data('world')
  m <- merge(world, rows[c('region', 'count')], by='region', all.x=TRUE)
  m <- m[order(m$order),]
  ggplot(m, aes(long, lat, group=group))+geom_polygon(aes(fill=count))+
    scale_fill_brewer(na.value='grey', drop=FALSE, labels=c('< 5', '5 - 10', '10 - 20', '20 - 30', '> 30'))+
      theme(axis.ticks = element_blank(),
            axis.text=element_blank(),
            axis.title=element_blank())+
              annotate("text", x=-160, y=0, label=rows$year[1], face='bold')
  ggsave(sprintf("tmp-%d.png", rows$year[1]), width=5, height=2.5)
})

## make animation: convert   -delay 60   -loop 0   tmp*png  country_hiv.gif
