#!/usr/bin/perl

#########################################################################
#   Autori:             Marco Colombo (marco@openit.it)
#                       Giuliano Natali Diaolin (diaolin@openit.it)
#   Copyright:          Open It S.r.l.
#                       Viale Dante, 78
#                       38057 Pergine Valsugana (TN) ITALY
#                       Tel: +39 0461 534800 Fax: +39 0461 538443
##############################################################################
# index.cgi

use File::Copy;

require './openvpn-lib.pl';

$mdir = &module_root_directory("openvpn");

my $version = `cat VERSION`;
my $availver = `cat current`;
$version =~ s/[^0-9\.]//g;
$availver =~ s/[^0-9\.]//g;

unless (-s $config{'openssl_home'}) { File::Copy::copy($mdir.'/openvpn-ssl.cnf',$config{'openssl_home'}); }

# Check if openvpn is actually installed
if (!-x $config{'openvpn_path'} or !-d $config{'openvpn_home'} or !$config{'openvpn_keys_subdir'} or !$config{'openvpn_clients_subdir'} or !$config{'openvpn_servers_subdir'}) {
	&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, 0,
		&help_search_link("openvpn", "man", "doc", "google").."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>");
	print &text('no_openvpn_path', "<tt>$config{'openvpn_path'}</tt>",
			  "$gconfig{'webprefix'}/config.cgi?$module_name"),"<p>\n";

	&foreign_require("software", "software-lib.pl");
	$lnk = &software::missing_install_link(
			"openvpn", $text{'index_openvpn'},
			"../$module_name/", $text{'title_opnvpn'});
	print $lnk.$text{'index_reconfigurepath'}."<p>\n" if ($lnk);

	&ui_print_footer("/", $text{'index'});
	exit;
}

# Check if AC is actually installed
if (!-x $config{'openssl_path'} or !-s $config{'openssl_home'}) {
	&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, 0,
		&help_search_link("openssl", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>");
	print &text('no_openssl_path', "<tt>$config{'openssl_path'}</tt>",
		  "$gconfig{'webprefix'}/config.cgi?$module_name"),"<p>\n";

	&foreign_require("software", "software-lib.pl");
	$lnk = &software::missing_install_link(
			"openssl", $text{'index_openssl'},
			"../$module_name/", $text{'index_header'});
	print $lnk.$text{'index_reconfigurepath'}."<p>\n" if ($lnk);

	&ui_print_footer("/", $text{'index'});
	exit;
}

if (!-d $config{'openvpn_home'}."/".$config{'openvpn_keys_subdir'}) {
    mkdir($config{'openvpn_home'}."/".$config{'openvpn_keys_subdir'},0755) || &error("Failed to create keys sub directory ".$config{'openvpn_home'}."/".$config{'openvpn_keys_subdir'}." : $!"); 
}

if (!-d $config{'openvpn_home'}."/".$config{'openvpn_clients_subdir'}) {
    mkdir($config{'openvpn_home'}."/".$config{'openvpn_clients_subdir'},0700) || &error("Failed to create clients sub directory ".$config{'openvpn_home'}."/".$config{'openvpn_clients_subdir'}." : $!"); 
}

if (!-d $config{'openvpn_home'}."/".$config{'openvpn_servers_subdir'}) {
    mkdir($config{'openvpn_home'}."/".$config{'openvpn_servers_subdir'},0755) || &error("Failed to create servers sub directory ".$config{'openvpn_home'}."/".$config{'openvpn_servers_subdir'}." : $!"); 
}

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef, 
		&help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>", 
		undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

# lista icone per pagine modulo
$df_icon = { "icon" => "images/listca.gif",
	     "name" => $text{'listca_title'},
	     "link" => "listca.cgi" };
$ht_icon = { "icon" => "images/listvpn.gif",
	     "name" => $text{'listserver_title'},
	     "link" => "listvpn.cgi" };
$ds_icon = { "icon" => "images/listactiveconnect.gif",
	     "name" => $text{'listactiveconnect_title'},
	     "link" => "listactiveconnect.cgi?all=1" };
&config_icons("global", $df_icon, $ht_icon, $ds_icon);

$isrun = &is_openvpn_running();
print "<hr>\n";
if ($isrun == 0) {
    print &ui_buttons_start();

    print &ui_buttons_row("actions.cgi",$text{'index_start'},$text{'index_startmsg'},&ui_hidden("action", "start"));

    print &ui_buttons_end();
} elsif ($isrun) {
    print &ui_buttons_start();

    print &ui_buttons_row("actions.cgi",$text{'index_restart'},$text{'index_restartmsg'},&ui_hidden("action", "restart"));
    print &ui_buttons_row("actions.cgi",$text{'index_stop'},$text{'index_stopmsg'},&ui_hidden("action", "stop"));

    print &ui_buttons_end();

}
print "<hr>\n";

&ui_print_footer("/", $text{'index'});
