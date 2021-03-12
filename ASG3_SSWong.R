# Load R Packages

library(shiny)
library(tidyr)
library(dplyr)
library(ggplot2)

# Load Data

mortality <- read.csv("https://raw.githubusercontent.com/charleyferrari/CUNY_DATA_608/master/module3/data/cleaned-cdc-mortality-1999-2010-2.csv", header=TRUE, sep=",")


# Data Preparation and Pre-processing

## Rank states by crude mortality for each cause of death

mortality_2010 <- mortality %>% 
  filter(Year==2010) %>% 
  select(State, Year, ICD.Chapter, Crude.Rate) %>% 
  arrange(ICD.Chapter)

mortality_2010[is.na(mortality_2010)] <- "District of Columbia"

## Check whether states are improving their mortality rates (per cause) over national average

mortality_avg <- mortality %>% 
  group_by(Year, ICD.Chapter) %>% 
  mutate(national_crude_rate = 10^5*(sum(Deaths)/sum(Population))) %>% 
  select(Year, State, ICD.Chapter, national_crude_rate, Crude.Rate) %>% 
  mutate(State_Name = state.name[match(State, state.abb)]) %>%
  arrange(ICD.Chapter)

mortality_avg[is.na(mortality_avg)] <- "District of Columbia"

mortality_avg <- mortality_avg %>% gather("National_State", 'value', national_crude_rate, Crude.Rate)


# Shiny App

ui <- fluidPage(
  
  tabsetPanel(
    
    tabPanel("Question 1",
    
      titlePanel(h2("States Ranking of Crude Mortality Rate for Each Cause of Death in 2010", align='left')), 
      sidebarLayout(position = "left", 
        sidebarPanel(
          selectInput("var1", 
                      label = "Choose a Cause of Death",
                      choices = mortality_2010$ICD.Chapter,
                      selected = "",
                      )),
        mainPanel(
          plotOutput("barplot1"))
        )),
  
    tabPanel("Question 2", 
       
        titlePanel(h2("Crude Mortality Rate, State Vs National, from Year 1999-2010", align='left')), 
        sidebarLayout(position = "left", 
          sidebarPanel(
            selectInput("var2", 
                        label = "Choose a State",
                        choices = mortality_avg$State_Name,
                        selected = ""
                        ), 
            
            selectInput("var3", 
                        label = "Choose a Cause of Death",
                        choices = mortality_avg$ICD.Chapter,
                        selected = "")),
          mainPanel(
            plotOutput("colplot2")))      
             
      )
    
  )  
  
)

server <- function(input, output) {
  output$barplot1 <- renderPlot({
    ggplot(mortality_2010[mortality_2010$ICD.Chapter==input$var1,], 
           aes(x=reorder(State, -Crude.Rate), y=Crude.Rate)) + 
      labs(x="", y = "Crude Death Rate per 100,000 Persons") + 
      geom_bar(stat='identity', fill="darkgray", border = 'white') +
      scale_y_continuous(breaks = scales::pretty_breaks(n=10)) +
      theme(
        panel.background = element_blank(), 
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        axis.text.x = element_text(angle=45, face="bold", size=11, vjust=1, hjust=1),
        axis.text.y = element_text(face="bold", size=11), 
        axis.title.y = element_text(margin = margin(t=0, r=20, b=0, l=0), size=12))},
    width='auto', height='auto')
    
    output$colplot2 <- renderPlot({
      ggplot(mortality_avg[mortality_avg$State_Name==input$var2 & mortality_avg$ICD.Chapter==input$var3,], 
             aes(x=Year, y=value, fill=National_State)) +
      labs(x="", y="Crude Death Rate per 100,000 Persons") +  
      geom_col(position=position_dodge()) +
      scale_fill_discrete(labels = c("State", "National")) + 
      scale_x_continuous(breaks = seq(1999,2010,1)) +
      scale_y_continuous(breaks = scales::pretty_breaks(n=10)) + 
      theme(
        panel.background = element_blank(), 
        legend.title = element_blank(),
        legend.position = "bottom",
        legend.text=element_text(size=12),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        axis.text.x = element_text(face="bold", size=12),
        axis.text.y = element_text(face="bold", size=12),
        axis.title.y = element_text(margin=margin(t=0, r=20, b=0, l=0), size=12))}, 
      width='auto', height='auto')
}

shinyApp(ui=ui, server=server)


