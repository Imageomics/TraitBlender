

displayCodePanel_ui <- function(){
  div(style = "overflow-y: auto; height: calc(100vh - 50px);", 
      
      verbatimTextOutput("code_display"),
      #textInput("new_code", "Enter new code here"),
      #actionButton("add_code", "Add code"),
      verbatimTextOutput("ordered_items")
  )
}


### Converts code_vec into the format that gets plotted
displayCodePanel_server <- function(){
  renderPrint({
    combined_code()
  })
}