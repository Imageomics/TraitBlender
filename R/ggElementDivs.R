
codeDiv <- function(){
  div(
    textInput("new_code", "Enter new code here"),
    actionButton("add_code", "Add code"),
    verbatimTextOutput("ordered_items")
  )
}