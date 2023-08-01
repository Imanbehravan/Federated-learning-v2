library("TCGAbiolinks")
library("SummarizedExperiment")


GDCprojects <- getGDCprojects()
TCGAbiolinks:::getProjectSummary("TCGA-BRCA")

query_TCGA_primary_tumor <- GDCquery(
  project = "TCGA-BRCA",
  data.category = "Transcriptome Profiling",
  data.type = "Gene Expression Quantification",
  experimental.strategy = "RNA-Seq",
  workflow.type = 'STAR - Counts',
  sample.type = "Primary Tumor")

output_query_primary_tumor <- getResults(query_TCGA_primary_tumor)

case_names <- output_query_primary_tumor$cases[1:100]

query_TCGA_solid_tumor <- GDCquery(
  project = "TCGA-BRCA",
  data.category = "Transcriptome Profiling",
  data.type = "Gene Expression Quantification",
  experimental.strategy = "RNA-Seq",
  workflow.type = 'STAR - Counts',
  sample.type = "Solid Tissue Normal")

output_query_solid_tumor <- getResults(query_TCGA_solid_tumor)

case_names[101:200] <- output_query_solid_tumor$cases[1:100]

query_main <- GDCquery(
  project = "TCGA-BRCA",
  data.category = "Transcriptome Profiling",
  data.type = "Gene Expression Quantification",
  experimental.strategy = "RNA-Seq",
  workflow.type = 'STAR - Counts',
  barcode = case_names)

output_query_main <- getResults(query_main)

tcga_data <- GDCprepare(query_main,summarizedExperiment = TRUE)
class(tcga_data)

brca_matrix <- assay(tcga_data, 'fpkm_unstrand')
transposed_data <- t(brca_matrix)

write.table(transposed_data, file = "Gene_expression_data.txt", append = FALSE, sep = ",", dec = ".",
            row.names = FALSE, col.names = FALSE)

train_data = unlist(transposed_data)
dim(train_data)
pcaout <- prcomp(train_data, scale. = F)

pcaoutdata <- pcaout$x
write.table(pcaoutdata, file = "Gene_expression_PCA_data.txt", append = FALSE, sep = ",", dec = ".",
            row.names = FALSE, col.names = FALSE)


