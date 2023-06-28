
mainTab_ui <- function(){
  tabPanel("Main", 
           sidebarLayout(
             # Sidebar with import buttons
             importData_ui(),
             
             # Main panel for plots and table
             mainPanel(
               
               shinyjs::useShinyjs(),
               
               tabsetPanel(
                 id = "tabs",
                 tabPanel("Tree",
                          plotOutput("plot1"),  # Plot
                          # Here
                          actionButton("edit_plot", "Edit Plot"),
                          actionButton("export_plot", "Export Plot")
                 ),  # Layout selection
                 tabPanel("Table",
                          DT::dataTableOutput("table1"),
                          actionButton("edit_table", "Edit Data"),
                          actionButton("export_table", "Export Data"))  # Table
               ),
             )
           )
  )
  
}