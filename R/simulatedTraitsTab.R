simulatedTraitsTab_ui <- function(){
  tabPanel("Simulated Traits",
           div(
             id = "right_sidebar_layout",
             tags$style("#right_sidebar_layout .container-fluid { flex-direction: row-reverse; }"),
             sidebarLayout(
               sidebarPanel(width = 3,
                            # Add your sidebar content here
               ),
               mainPanel(
                 plotOutput("phy_tree"),
                 actionButton("import_images_button", "Import Images")
               )
             )
           )
  )
}
