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
print "<form action=log_vpn.cgi>\n";
print "<input type=hidden name=\"vpn\" value=\"".$in{'vpn'}."\">\n";
print "<input type=hidden name=\"remove\" value=\"1\">\n";
print "<table width=100%><tr>\n";
print "<td><input type=submit value=\"$text{'empty_log'}\"></td>\n";
print "<td>$text{'empty_logmsg'}</td>\n";
print "</tr></table></form>\n";

print "<hr>\n";

print "<BR>";
&ui_print_footer("listvpn.cgi",$text{'list_server_vpn'});

##############################################################################33

sub filter_form {
    print "<form action=log_vpn.cgi style='margin-left:1em'>\n";
    print "<input type=hidden name=vpn value='$in{'vpn'}'>\n";

    print &text('view_header', "<input name=lines size=3 value='$lines'>",
	"<tt>".&html_escape($in{'vpn'})."</tt>"),"\n";
    print "&nbsp;&nbsp;\n";
    print &text('view_filter', "<input name=filter size=15 value='$in{'filter'}'>"),"\n";
    print "&nbsp;&nbsp;\n";
    print "<input type=submit value='$text{'view_refresh'}'></form>\n";
}
