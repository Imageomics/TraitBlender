
importData_ui <- function(){
  
  sidebarPanel(
    
    # Import Newick file button
    fileInput("file2", "Import Tree",
              multiple = TRUE,
              accept = c("text/plain",
                         ".newick",
                         ".tre",
                         ".tree")),
    
    # Import CSV button
    fileInput("file1", 
              "Import Character Data",
              accept = c("text/csv",
                         "text/comma-separated-values,text/plain",
                         ".csv",
                         "text/tab-separated-values,text/plain",
                         ".tsv",
                         "application/vnd.ms-excel",
                         ".xls",
                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                         ".xlsx",
                         ".nexus",
                         ".nex"))
    ,
    
    # Text box for R code
    textAreaInput("text1", "Enter R code", "", rows = 10),
  )
  
}


