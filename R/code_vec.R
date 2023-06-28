
#define the code vector

code_vec <- reactiveVal(list("ggtree(phy(), layout = input$layout) + theme_tree2()", rep("", 16)))
  