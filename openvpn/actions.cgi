#!/usr/bin/perl

#########################################################################
#   Autori:             Marco Colombo (marco@openit.it)
#                       Giuliano Natali Diaolin (diaolin@openit.it)
#   Copyright:          Open It S.r.l.
#                       Viale Dante, 78
#                       38057 Pergine Valsugana (TN) ITALY
#                       Tel: +39 0461 534800 Fax: +39 0461 538443
##############################################################################

require './openvpn-lib.pl';

#my $wgettmpfile="/tmp/ovpnadmwget.log";				# to check for errors while downloading
#my $wgetcmd="wget -N"; 						# only download if online file is newer
#my $wgeturl="http://www.iks.hs-merseburg.de/~hspaethe/ovpnadm";	# source address with path	(change it to your needs)
#my $wgetfile="current";						# file to download, is version-number is compared to VERSION

# legge parametri da form o da url e li inserisce in hash $in
&ReadParse();

if ($in{'action'} eq "start" and $config{'start_cmd'}) {
    $rv = &system_logged("$config{'start_cmd'} >/dev/null 2>&1 </dev/null");
    if ($rv) { &error(&text('start_fail', $config{'start_cmd'})); }
} elsif ($in{'action'} eq "stop" and $config{'stop_cmd'}) {
    $rv = &system_logged("$config{'stop_cmd'} >/dev/null 2>&1 </dev/null");
    if ($rv) { &error(&text('stop_fail', $config{'stop_cmd'})); }
} elsif ($in{'action'} eq "restart" and $config{'stop_cmd'} and $config{'start_cmd'}) {
    $rv = &system_logged("$config{'stop_cmd'} >/dev/null 2>&1 </dev/null");
    if ($rv) { &error(&text('stop_fail', $config{'stop_cmd'})); }
    $rv = &system_logged("$config{'start_cmd'} >/dev/null 2>&1 </dev/null");
    if ($rv) { &error(&text('start_fail', $config{'start_cmd'})); }
#} elsif ($in{'action'} eq "check") {
#        &system_logged("$wgetcmd $wgeturl/$wgetfile > $wgettmpfile 2>&1");      # check the online file
#        $rv = &system_logged("grep 'ERROR [4][0-9][0-9]' $wgettmpfile");        # any errors during download?
#        if ( ! $rv ) {
#            &error("HTTP error ", $rv);                                         # show the error to the user
#	}
} else {
    &error(&text('cmdabsent'));
}

&redirect("index.cgi");