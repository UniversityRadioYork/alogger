TAR_INC = logger.py .git version Makefile .gitignore README
TAR_VER = `cat version`

alogger-$(TAR_VER) : $(TAR_INC)
	tar -cvzf alogger-$(TAR_VER).tar.gz $(TAR_INC) 

clean:
	rm alogger-*.tar.gz
