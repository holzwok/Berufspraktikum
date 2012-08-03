counts = read.table("C:/Users/MJS/Dropbox/Studium/Berufspraktikum/Project_Aouefa_Expression_network/RNA_count_data.csv", header=TRUE, sep = ",")

count = counts$count
CLB5 = counts$CLB5
CLN2 = counts$CLN2
SIC1 = counts$SIC1

x = unlist(mapply(rep, count, CLB5))
y = unlist(mapply(rep, count, CLN2))
z = unlist(mapply(rep, count, SIC1))

#poisson.m(x)
poisson.mtest(x)
#poisson.m(y)
poisson.mtest(y)
#poisson.m(z)
poisson.mtest(z)
