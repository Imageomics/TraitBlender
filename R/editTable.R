

editTable_ui <- function(){
  bsModal(id='Table2', title='Character Data', trigger="edit_table", size='large',
          withSpinner(dataTableOutput("table2")))
}