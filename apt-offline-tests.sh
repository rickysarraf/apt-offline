#!/bin/sh

DISLIKED_PACKAGES="emacs eclipse gnome"
RELEASE="unstable"
URI="/tmp/set-$PPID.uris"
CACHE_DIR="/var/cache/apt/archives"
DOWNLOAD_DIR="/tmp/apt-offline-tests-$PPID"
BUNDLE_FILE="/tmp/apt-offline-tests-$PPID.zip"
THREADS=5
APT_OFFLINE="./apt-offline"

set_features () {
	echo "Executing command 'set $URI'"
	$APT_OFFLINE set $URI

	echo "Executing command 'set $URI --simulate --verbose'"
	$APT_OFFLINE set $URI --simulate --verbose

	echo "Executing command 'set $URI --update'"
	$APT_OFFLINE set $URI --update

	echo "Executing command 'set $URI --upgrade'"
	$APT_OFFLINE set $URI --upgrade

	echo "Executing command 'set $URI --update --upgrade'"
	$APT_OFFLINE set $URI --update --upgrade

	echo "Executing command 'set $URI --update --upgrade --upgrade-type upgrade'"
	$APT_OFFLINE set $URI --update --upgrade --upgrade-type upgrade

	echo "Executing command 'set $URI --update --upgrade --upgrade-type upgrade --release $RELEASE'"
	$APT_OFFLINE set $URI --update --upgrade --upgrade-type upgrade --release $RELEASE 

	echo "Executing command 'set $URI --install-packages $DISLIKED_PACKAGES'"
	$APT_OFFLINE set $URI --install-packages $DISLIKED_PACKAGES

	echo "Executing command 'set $URI --install-packages $DISLIKED_PACKAGES --release $RELEASE'"
	$APT_OFFLINE set $URI --install-packages $DISLIKED_PACKAGES --release $RELEASE

	echo "Executing command 'set $URI --install-src-packages $DISLIKED_PACKAGES'"
	$APT_OFFLINE set $URI --install-src-packages $DISLIKED_PACKAGES

	echo "Executing command 'set $URI --install-src-packages $DISLIKED_PACKAGES --release $RELEASE'"
	$APT_OFFLINE set $URI --install-src-packages $DISLIKED_PACKAGES --release $RELEASE

	echo "Executing command 'set $URI --src-build-dep --install-src-packages $DISLIKED_PACKAGES'"
	$APT_OFFLINE set $URI --src-build-dep --install-src-packages $DISLIKED_PACKAGES

	echo "Executing command 'set $URI --src-build-dep --install-src-packages $DISLIKED_PACKAGES --release $RELEASE'"
	$APT_OFFLINE set $URI --src-build-dep --install-src-packages $DISLIKED_PACKAGES --release $RELEASE

}

get_features () {
	echo "Executing command 'get $URI --verbose'"
	$APT_OFFLINE get $URI --verbose

	echo "Executing command 'get $URI --threads $THREADS'"
	$APT_OFFLINE get $URI --threads $THREADS

	echo "Executing command 'get $URI --threads $THREADS --socket-timeout 30'"
	$APT_OFFLINE get $URI --threads $THREADS --socket-timeout 30

	echo "Executing command 'get $URI --threads $THREADS -d $DOWNLOAD_DIR'"
	$APT_OFFLINE get $URI --threads $THREADS -d $DOWNLOAD_DIR

	echo "Executing command 'get $URI --threads $THREADS -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR'"
	$APT_OFFLINE get $URI --threads $THREADS -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR

	echo "Executing command 'get $URI --no-checksum -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR'"
	$APT_OFFLINE get $URI --no-checksum -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR

	echo "Executing command 'get $URI --bug-reports --threads $THREADS -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR'"
	$APT_OFFLINE get $URI --threads $THREADS --bug-reports -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR

	echo "Executing command 'get $URI --bug-reports --threads $THREADS --bundle $BUNDLE_FILE -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR'"
	$APT_OFFLINE get $URI --threads $THREADS --bug-reports -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR --bundle $BUNDLE_FILE

}

install_features () {
	echo "Executing command 'install $URI --verbose --skip-bug-reports'"
	$APT_OFFLINE install $URI --verbose --skip-bug-reports

	echo "Executing command 'install $URI --simulate --skip-bug-reports'"
	$APT_OFFLINE install $URI --simulate --skip-bug-reports

	echo "Executing command 'install $URI --skip-bug-reports'"
	$APT_OFFLINE install $URI --simulate --skip-bug-reports

	echo "Executing command 'install $URI --skip-bug-reports --allow-unauthenticated'"
	$APT_OFFLINE install $URI --simulate --skip-bug-reports  --allow-unauthenticated
}

install_features_prompt () {
	echo "Executing command 'install $URI --verbose '"
	$APT_OFFLINE install $URI --verbose 

	echo "Executing command 'install $URI --simulate '"
	$APT_OFFLINE install $URI --simulate 

	echo "Executing command 'install $URI '"
	$APT_OFFLINE install $URI

	echo "Executing command 'install $URI --allow-unauthenticated'"
	$APT_OFFLINE install $URI --allow-unauthenticated
}

all_features () {
	echo "Executing function set_features"
	set_features

	echo "Executing function get_features"
	get_features

	echo "Executing function install_features"
	install_features
}

case $1 in
	"set")
		set_features
		;;
	"get")
		get_features
		;;
	"install")
		install_features
		;;
	"install_features_prompt")
		install_features_prompt
		;;
	"--help")
		echo "$0 [set || get || install || install_features_prompt]"
		exit 0;
		;;
	"-h")
		echo "$0 [set || get || install || install_features_prompt]"
		exit 0;
		;;
	*)
		all_features
		;;
esac

