FC           = gfortran
FCFLAGS      = -O3 -Wall -Wextra
F2PYC        = python3 -m numpy.f2py
F2PYFLAGS    = --fcompiler=gnu95 -I.  #if libraries, include -L/path
F2PY_TARGET  = sampling

#we'll compile the f2py target seperately (using f2py not gfortran)
SOURCES = $(filter-out ./${F2PY_TARGET}.f90, $(wildcard ./*.f90))
OBJS    = $(SOURCES:.f90=.o)

#all, one rule to rule them all
all: ${OBJS}
	${F2PYC} -c ${F2PYFLAGS} ${OBJS} -m ${F2PY_TARGET} ${F2PY_TARGET}.f90

%.o: %.f90
	${FC} -shared ${FCLAGS} -fPIC -c $< -o $@

# Clean target
clean:
	rm -f ./*.o
	rm -f ./*.mod
	rm -f ./*.so

# Phony targets
.PHONY: all clean
