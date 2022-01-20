main: input.o matrix.o main.o
	g++ main.o input.o matrix.o -o main `pkg-config --libs eigen3 liblzma`

main.o: main.cpp matrix.h input.h
	g++ -g -c main.cpp -o main.o `pkg-config --cflags eigen3 liblzma`

input.o: input.cpp input.h
	g++ -g -c input.cpp -o input.o `pkg-config --cflags eigen3 liblzma`

matrix.o: matrix.cpp matrix.h
	g++ -g -c matrix.cpp -o matrix.o `pkg-config --cflags eigen3 liblzma`
