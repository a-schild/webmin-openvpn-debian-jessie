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

&foreign_require("proc", "proc-lib.pl");

# legge parametri da form o da url e li inserisce in hash $in
&ReadParse();

# Viewing a log file
$log = $config{'openvpn_home'}.'/'.$config{'openvpn_servers_subdir'}.'/'.$in{'vpn'}.'/logs/openvpn.log';

# azzera il file di log e ritorna alla lista
if ($in{'remove'} == 1) { open F,">$log"; close F; &redirect("listvpn.cgi"); }

if (int($in{'lines'}) > 0) { $lines = int($in{'lines'}); } else { $lines = $config{'log_lines'}; }
if ($in{'filter'}) { $filter = quotemeta($in{'filter'}); } else { $filter = ""; }

if ($config{'log_refresh'}) { print "Refresh: $config{'log_refresh'}\r\n" }

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

print "<BR>";

# start tabella
print "<table border width=100%>\n";
# title row
print "<tr $tb>";
    print "<td nowrap><b>".$text{'title_log_server_vpn'}.' '.$in{'vpn'}."</b></td>\n";
print "</tr>\n";

print "<tr $tb>";
    print "<td nowrap>\n";
    &filter_form();
    print "</td>\n";
print "</tr>\n";

print "</table>";

print "<BR>";

$| = 1;
print "<pre>";
local $tailcmd = $config{'tail_cmd'} || "tail -n LINES";
$tailcmd =~ s/LINES/$lines/g;

if (-s $log) {
    if ($filter ne "") {
	$got = &foreign_call("proc", "safe_process_exec","grep -i $filter $log | $tailcmd",0, 0, STDOUT, undef, 1);
    } else {
	$got = &foreign_call("proc", "safe_process_exec","$tailcmd $log", 0, 0, STDOUT, undef, 1);
    }
} else { $got = ""; }

if (!$got) { print "$text{'view_log_empty'}\n"; }
print "</pre>\n";

print "<BR>";

# start tabella
print "<table border width=100%>\n";
print "<tr $tb>";
    print "<td nowrap>\n";
    &filter_form();
    print "</td>\n";
print "</tr>\n";
print "</table>";

print "<BR>";

print "<hr>\n";

print &ui_buttons_start();

print &ui_buttons_row("log_vpn.cgi",$text{'empty_log'},$text{'empty_logmsg'},&ui_hidden("vpn", $in{'vpn'}).&ui_hidden("remove", "1"));

print &ui_buttons_end();

print "<hr>\n";

print "<BR>";
&ui_print_footer("listvpn.cgi",$text{'list_server_vpn'});

##############################################################################33

sub filter_form {
    print &ui_form_start("log_vpn.cgi", "POST");
    print &ui_hidden('vpn',$in{'vpn'});

    print &ui_table_start();
    print &ui_table_row($text{'view_header'}, &ui_textbox('lines',$lines,3),&html_escape($in{'vpn'}))."</tr>\n";
    print &ui_table_row($text{'view_filter'}, &ui_textbox('filter',$in{'filter'},15))."</tr>\n";
    print &ui_table_end();
    print &ui_form_end([ [ undef, $text{'view_refresh'} ] ]);

}
