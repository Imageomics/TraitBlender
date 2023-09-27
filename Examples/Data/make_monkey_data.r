# Load the necessary libraries
library(ape)
library(geiger)
library(phytools)

setwd("D://TraitBlender/TraitBlender")

# Generate a random phylogenetic tree with 100 tips
tree <- rtree(100)

# Generate normally distributed branch lengths
#tree$edge.length <- abs(rnorm(n = tree$Nnode, mean = 1, sd = 0.5))


# Make the tree ultrametric using a molecular clock
tree <- chronos(tree)
# Scale the tree to artificially lengthen branches
tree$edge.length <- tree$edge.length * 40

# Visualize the tree
plot(tree)

# Create a rate matrix (Q) for 3 states (0, 1, 2)
Q <- matrix(c(
  -4, 2, 2,
  2, -4, 2,
  2, 2, -4
), nrow=3, ncol=3)
rownames(Q) <- colnames(Q) <- 0:2


# Simulate discrete trait evolution
trait <- rTraitDisc(tree, Q=Q, states=as.character(0:3))


# Generate data for continuous traits evolving under Brownian motion
jowl_size <- rTraitCont(tree, model="BM", sigma=0.005, root.value=1.1)
dome_size <- rTraitCont(tree, model="BM", sigma=0.1, root.value=1.1)
overall_size <- rTraitCont(tree, model="BM", sigma=0.2, root.value=1.1)

# Generate data for the discrete trait (ear color)
# Make it equally easy to switch between any two states.
Q <- matrix(c(
  -2, 1, 1,
  1, -2, 1,
  1, 1, -2
), nrow=3, ncol=3)
rownames(Q) <- colnames(Q) <- as.character(0:2)

ear_color <- rTraitDisc(tree, Q=Q, states=as.character(0:2))

# Create the dataset
dataset <- data.frame(
  label=tree$tip.label,
  Jowl_Size=jowl_size,
  Dome_Size=dome_size,
  Overall_Size=overall_size,
  vertex_group_csv="D://TraitBlender/TraitBlender/Examples/Data/suzanne.csv",
  ear_color=ear_color
)

# Save the dataset to a CSV file
write.csv(dataset, file="Examples/Data/monkey_data.csv", row.names=FALSE)
write.tree(tree, file="Examples/Data/monkey_tree.nwk")

# Add the simulated trait to the tree tip labels for visualization
tree$tip.label <- paste0(tree$tip.label, "_", trait)

# Plot the tree with trait states
plot(tree)
View(dataset)