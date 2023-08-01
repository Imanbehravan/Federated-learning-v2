# script to download data from TCGA using TCGAbiolinks
# setwd("~/Desktop/demo/TCGAbiolinks")


library(TCGAbiolinks)
#library(tidyverse)
#library(maftools)
#library(pheatmap)
library(SummarizedExperiment)


# get a list of projects
gdcprojects <- getGDCprojects()
getProjectSummary('TCGA-BRCA')



# building a query

query_TCGA <- GDCquery(project = 'TCGA-BRCA',
                       data.category = 'Transcriptome Profiling',
                       experimental.strategy = 'RNA-Seq',
                       workflow.type = 'STAR - Counts',
                       access = 'open',
                       barcode = c('TCGA-LL-A73Y-01A-11R-A33J-07', 'TCGA-E2-A1IU-01A-11R-A14D-07','TCGA-AO-A03U-01B-21R-A10J-07'))

getResults(query_TCGA)

# download data - GDCdownload
GDCdownload(query_TCGA)


# prepare data
tcga_brca_data <- GDCprepare(query_TCGA, summarizedExperiment = TRUE)
brca_matrix <- assay(tcga_brca_data, 'fpkm_unstrand')

