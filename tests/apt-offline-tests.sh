#!/bin/sh

DISLIKED_PACKAGES="lxde icewm eclipse"
RELEASE=`lsb_release -c -s`
DIR="$(mktemp --tmpdir --directory apt-offline-tests-XXXXXXXX)"
cleanup () { rm --recursive --force "$DIR"; }
trap cleanup EXIT
URI="$DIR/set.uris"
CACHE_DIR="/var/cache/apt/archives"
DOWNLOAD_DIR="$DIR/download-dir"
BUNDLE_FILE="$DIR/bundle-file.zip"
THREADS=5
APT_OFFLINE="./apt-offline "

run()
{
    echo "Executing command: $1"
    $1
}

set_features () {
	if [ ! -z $1 ]; then
		URI=$1
	fi

	run "$APT_OFFLINE set $URI"

	run "$APT_OFFLINE set $URI --simulate"

	run "$APT_OFFLINE set $URI --update"

	run "$APT_OFFLINE set $URI --upgrade"

	run "$APT_OFFLINE set $URI --update --upgrade"

	run "$APT_OFFLINE set $URI --update --upgrade --upgrade-type upgrade"

	run "$APT_OFFLINE set $URI --update --upgrade --upgrade-type upgrade --release $RELEASE"

	run "$APT_OFFLINE set $URI --install-packages $DISLIKED_PACKAGES"

	run "$APT_OFFLINE set $URI --install-packages $DISLIKED_PACKAGES --release $RELEASE"

	run "$APT_OFFLINE set $URI --install-src-packages $DISLIKED_PACKAGES"

	run "$APT_OFFLINE set $URI --install-src-packages $DISLIKED_PACKAGES --release $RELEASE"

	run "$APT_OFFLINE set $URI --src-build-dep --install-src-packages $DISLIKED_PACKAGES"

	run "$APT_OFFLINE set $URI --src-build-dep --install-src-packages $DISLIKED_PACKAGES --release $RELEASE"

}

get_features () {
	if [ ! -z $1 ]; then
		URI=$1
	fi

	run "$APT_OFFLINE get $URI"

	run "$APT_OFFLINE get $URI --threads $THREADS"

	run "$APT_OFFLINE get $URI --threads $THREADS --socket-timeout 30"

	run "$APT_OFFLINE get $URI --threads $THREADS -d $DOWNLOAD_DIR"

	run "$APT_OFFLINE get $URI --threads $THREADS -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR"

	run "$APT_OFFLINE get $URI --no-checksum -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR"

	run "$APT_OFFLINE get $URI --threads $THREADS --bug-reports -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR"

	run "$APT_OFFLINE get $URI --threads $THREADS --bug-reports -d $DOWNLOAD_DIR --cache-dir $CACHE_DIR --bundle $BUNDLE_FILE"

}

install_features () {
	if [ ! -z $1 ]; then
		DOWNLOAD_DIR=$1
		BUNDLE_FILE=$1
	fi

	run "$APT_OFFLINE install $DOWNLOAD_DIR  --skip-bug-reports"

	run "$APT_OFFLINE install $DOWNLOAD_DIR --simulate --skip-bug-reports"

	run "$APT_OFFLINE install $DOWNLOAD_DIR --simulate --skip-bug-reports"

	run "$APT_OFFLINE install $DOWNLOAD_DIR --simulate --skip-bug-reports  --allow-unauthenticated"

	run "$APT_OFFLINE install $BUNDLE_FILE  --skip-bug-reports"

	run "$APT_OFFLINE install $BUNDLE_FILE --simulate --skip-bug-reports"

	run "$APT_OFFLINE install $BUNDLE_FILE --simulate --skip-bug-reports"

	run "$APT_OFFLINE install $BUNDLE_FILE --simulate --skip-bug-reports  --allow-unauthenticated"
}

install_features_prompt () {
	if [ ! -z $1 ]; then
		DOWNLOAD_DIR=$1
		BUNDLE_FILE=$1
	fi

	run "$APT_OFFLINE install $DOWNLOAD_DIR"

	run "$APT_OFFLINE install $DOWNLOAD_DIR --simulate"

	run "$APT_OFFLINE install $DOWNLOAD_DIR --simulate"

	run "$APT_OFFLINE install $DOWNLOAD_DIR --simulate --allow-unauthenticated"

	run "$APT_OFFLINE install $BUNDLE_FILE"

	run "$APT_OFFLINE install $BUNDLE_FILE --simulate"

	run "$APT_OFFLINE install $BUNDLE_FILE --simulate"

	run "$APT_OFFLINE install $BUNDLE_FILE --simulate --allow-unauthenticated"
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
		if [ ! -z $2 ]; then
			set_features $2
		else
			set_features
		fi
		;;
	"get")
		if [ ! -z $2 ]; then
			get_features $2
		else
			get_features
		fi
		;;
	"install_features_promptless")
		if [ ! -z $2 ]; then
			install_features $2
		else
			install_features
		fi
		;;
	"install")
		# With prompts for bug reports
		if [ ! -z $2 ]; then
			install_features_prompt $2
		else
			install_features_prompt
		fi
		;;
	"--help")
		echo "$0 [set || get || install_features_promptless || install]"
		exit 0;
		;;
	"-h")
		echo "$0 [set || get || install_features_promptless || install]"
		exit 0;
		;;
	*)
		all_features
		;;
esac

