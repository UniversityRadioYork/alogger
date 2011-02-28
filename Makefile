TAR_INC = alogger .git version Makefile .gitignore README alogger-icon.png
TAR_VER = `cat version`

alogger-$(TAR_VER) : $(TAR_INC)
	tar -cvzf alogger-$(TAR_VER).tar.gz $(TAR_INC) 

clean:
	rm -f alogger-*.tar.gz *.raw
