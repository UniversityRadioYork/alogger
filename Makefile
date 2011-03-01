TAR_INC = src resources .git version Makefile .gitignore README AUTHORS ChangeLog COPYING
TAR_VER = `cat version`

alogger-$(TAR_VER) : $(TAR_INC)
	tar -cvzf alogger-$(TAR_VER).tar.gz $(TAR_INC) 

clean:
	rm -f alogger-*.tar.gz *.raw *.pyc
