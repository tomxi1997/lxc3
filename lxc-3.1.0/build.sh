export CBA_HOME=$ODMDIR
export PREFIX=$CBA_HOME

make distclean

./autogen.sh

CPPFLAGS="$CPPFLAGS $CFLAGS" \
./configure --host=$BUILD_TARGET_HOST --enable-shared=yes --enable-static=yes \
	--disable-api-docs \
	--disable-selinux \
	--disable-seccomp \
	--disable-werror \
	--disable-capabilities \
	--disable-examples \
	--disable-lua \
	--disable-python \
	--disable-bash \
	--enable-configpath-log \
        \
        --disable-doc \
        --disable-api-docs \
	\
	--prefix=$PREFIX \
	--with-systemdsystemunitdir=$PREFIX/lib/systemd/system \
	--with-config-path=$CBA_HOME/containers \
	--with-global-conf=$CBA_HOME/.config \
	--with-runtime-path=$PREFIX/cache

make -j8
sudo make install
