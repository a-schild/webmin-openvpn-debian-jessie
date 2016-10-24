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

print "<hr>\n";

# form per nuova CA
print &ui_form_start("create_ca.cgi", "POST");
print &ui_table_start($text{'newca_title'});
print &ui_table_row($text{'ca_ca_name'}, &ui_textbox('CA_NAME','changeme',50),'',[ 'nowrap',1 ])."</tr>\n";
print "<tr>".&ui_table_row($text{'ca_key_config'}, &ui_textbox('KEY_CONFIG',$config{'openssl_home'},50),'',[ 'nowrap',1 ])."</tr>\n";
print "<tr>".&ui_table_row($text{'ca_key_dir'}, $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'},'',[ 'nowrap',1 ])."</tr>\n";
print "<tr>".&ui_table_row($text{'ca_key_size'}, &ui_select('KEY_SIZE', 2048, [ [1024,1024 ], [2048,2048], [4096,4096] ]),'',[ 'nowrap',1 ])."</tr>\n";
print "<tr>".&ui_table_row($text{'ca_ca_expire'}, &ui_textbox('CA_EXPIRE', '3650',50),'',[ 'nowrap',1 ])."</tr>\n";
print "<tr>".&ui_table_row($text{'country'}, &ui_textbox('KEY_COUNTRY', 'US',50),'',[ 'nowrap',1 ])."</tr>\n";
print "<tr>".&ui_table_row($text{'province'}, &ui_textbox('KEY_PROVINCE', 'NY',50),'',[ 'nowrap',1 ])."</tr>\n";
print "<tr>".&ui_table_row($text{'city'}, &ui_textbox('KEY_CITY', 'New York',50),'',[ 'nowrap',1 ])."</tr>\n";
print "<tr>".&ui_table_row($text{'org'}, &ui_textbox('KEY_ORG', 'My Org',50),'',[ 'nowrap',1 ])."</tr>\n";
print "<tr>".&ui_table_row($text{'email'}, &ui_textbox('KEY_EMAIL', 'me@my.org',50),'',[ 'nowrap',1 ])."\n";
print &ui_table_end();
print &ui_form_end([ [ "save", $text{'save'} ] ]);

$isrun = &is_openvpn_running();
print "<hr>\n";
print "<table width=100%>\n";
if ($isrun == 0) {
    print "<tr valign=\"middle\"><form action=actions.cgi><td>\n";
    print "<input type=hidden name=action value=start>\n";
    print "<input type=submit value=\"$text{'index_start'}\"></td>\n";
    print "<td>$text{'index_startmsg'}</td>\n";
    print "</form></tr>\n";
} elsif ($isrun) {
    print "<tr valign=\"middle\"><form action=actions.cgi><td>\n";
    print "<input type=hidden name=action value=restart>\n";
    print "<input type=submit value=\"$text{'index_restart'}\"></td>\n";
    print "<td>$text{'index_restartmsg'}</td>\n";
    print "</form></tr>\n";

    print "<tr valign=\"middle\"><form action=actions.cgi><td>\n";
    print "<input type=hidden name=action value=stop>\n";
    print "<input type=submit value=\"$text{'index_stop'}\"></td>\n";
    print "<td>$text{'index_stopmsg'}</td>\n";
    print "</form></tr>\n";
}

# This check should be implemented adding the wget url into config file.
# Due to time problems we hope to implement it in the next version.
# At this time checking via third party modules is enough.
# For Hans: if you want to readd this feature please insert the wget url 
# into config file.   
#print "<tr valign=\"middle\"><form action=actions.cgi><td>\n";
#print "<input type=hidden name=action value=check>\n";
#print "<input type=submit value=\"$text{'index_check'}\"></td>\n";
#print "<td>";
#if (( $version != $availver ) && ( $availver != "" )){
#    print "$text{'index_updatemsg'} (".$availver.")\n";
#} else {
#    print "$text{'index_checkmsg'}\n";
#}
#print "</td>\n";
#print "</form></tr>\n";
print "</table>\n";
print "<hr>\n";
