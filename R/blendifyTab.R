# UI
blendifyTab_ui <- function(){
  tabPanel("Blendify",
           sidebarLayout(
             sidebarPanel(
               class = "blendifySidebar",
               uiOutput("scrollableList"),
               actionButton('addButton', label = HTML("<i class='fa fa-plus'></i>"), class = "btn btn-primary"),
               actionButton('launchBlenderButton', 'Launch Blender', class = "btn btn-primary")
             ),
             mainPanel(
               tabsetPanel(
                 id = "blendifyTabs",
                 tabPanel("Define Mapping"
                          # Add content for the Define Mapping tab here
                 ),
                 tabPanel("Preview Meshes",
                          selectInput("meshSelect", "Select a mesh", choices = NULL, selected = "suzanne")
                 ),
                 tabPanel("Explore"
                          # Add content for the Explore tab here
                 )
               )
             )
           )
  )
}
