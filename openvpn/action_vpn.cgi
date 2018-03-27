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

# legge parametri da form o da url e li inserisce in hash $in
&ReadParse();

if ($in{'action'} eq "start" and $config{'start_cmd'}) {
    $rv = &system_logged(sprintf($config{'start_cmd'},$in{'vpn'}).">/dev/null 2>&1 </dev/null");
    if ($rv) { &error(&text('start_fail', sprintf($config{'start_cmd'},$in{'vpn'}))); }
} elsif ($in{'action'} eq "stop" and $config{'stop_cmd'}) {
    $rv = &system_logged(sprintf($config{'stop_cmd'},$in{'vpn'})." >/dev/null 2>&1 </dev/null");
    if ($rv) { &error(&text('stop_fail', sprintf($config{'stop_cmd'},$in{'vpn'}))); }
} elsif ($in{'action'} eq "enable") {
    rename($config{'openvpn_home'}.'/'.$in{'vpn'}.'.disabled',$config{'openvpn_home'}.'/'.$in{'vpn'}.'.conf');
} elsif ($in{'action'} eq "disable") {
    # se attiva fermo
#    if (-s $config{'openvpn_pid_path'}.'/openvpn.'.$in{'vpn'}.'.pid') {
    if (-s $config{'openvpn_pid_path'}.'/'.$config{'openvpn_pid_prefix'}.$in{'vpn'}.'.pid') {
	$rv = &system_logged("$config{'stop_cmd'} $in{'vpn'} >/dev/null 2>&1 </dev/null");
        if ($rv) { &error(&text('stop_fail', $config{'stop_cmd'}.' '.$in{'vpn'})); }
    }
    # disabilito
    rename($config{'openvpn_home'}.'/'.$in{'vpn'}.'.conf',$config{'openvpn_home'}.'/'.$in{'vpn'}.'.disabled');
} else {
    &error(&text('cmdabsent'));
}

&redirect("listvpn.cgi");