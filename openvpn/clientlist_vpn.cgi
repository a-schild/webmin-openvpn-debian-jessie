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

&ReadVPNConf();

&ReadFieldsCA($in{'ca'});

$listvpn = &ReadClient();

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

print "<BR>";

# start tabella
print "<table border width=100%>\n";
# title row
print "<tr $tb>";
    print "<td colspan='7' nowrap><b>".$text{'list_client_vpn'}." ".$in{'vpn'}.":</b></td>\n";
print "</tr>\n";

# th row
print "<tr $tb>";
if (keys %{$listvpn}) {
    print "<td width='40%' nowrap><b>".$text{'name'}."</b></td>\n";
    print "<td nowrap><b>".$text{'h_ca'}."</b></td>\n";
    print "<td nowrap><b>".$text{'h_protocol'}."</b></td>\n";
    print "<td nowrap><b>".$text{'h_port'}."</b></td>\n";
    print "<td nowrap><b>".$text{'export'}."</b></td>\n";
    print "<td nowrap><b>".$text{'export'}."</b></td>\n";
    print "<td nowrap><b>".$text{'remove'}."</b></td>\n";
} else {
    print "<td colspan=6 nowrap align=center><b>".$text{'list_client_empty'}."</b></td>\n";
}
print "</tr>\n";
# rows
foreach $key (sort keys %{$listvpn}) {
    print "<tr $cb>\n";
	print "<td nowrap><a href=\"modify_client.cgi?vpn=".$in{'vpn'}."&client=".$$listvpn{$key}{CLIENT_NAME}."\" title=\"".$text{'modifyclient'}."\">".$$listvpn{$key}{CLIENT_NAME}."</a></td>\n";
	foreach $k (qw/CA_NAME proto port/) {
	    if ($$listvpn{$key}{$k}) {
		print "<td nowrap>".$$listvpn{$key}{$k}."</td>\n";
	    } else {
		print "<td>&nbsp;</td>\n";
	    }
	}
	print "<td nowrap>";
	print "<a href=\"export_client.cgi?vpn=".$in{'vpn'}."&client=".$$listvpn{$key}{CLIENT_NAME}."&format=archive\" title=\"".$text{'export_client_archive'}."\">".$text{'export_client_archive'}."</a>";
	print "</td>\n";
	print "<td nowrap>";
	print "<a href=\"export_client.cgi?vpn=".$in{'vpn'}."&client=".$$listvpn{$key}{CLIENT_NAME}."&format=single\" title=\"".$text{'export_client_single'}."\">".$text{'export_client_single'}."</a>";
	print "</td>\n";
	print "<td nowrap><a href=\"remove_client.cgi?vpn=".$in{'vpn'}."&client=".$$listvpn{$key}{CLIENT_NAME}."\" title=\"".$text{'removeclient'}."\">".$text{'remove'}."</a></td>\n";
    print "</tr>\n";
}
# stop tabella
print "</table>\n";
print "<BR>";
print "<hr>\n";

print &ui_buttons_start();
print &ui_buttons_row("new_client.cgi",$text{'new_client_title'},$text{'new_clientmsg'}." ".$in{'vpn'},&ui_hidden("vpn", $in{'vpn'}));
print &ui_buttons_end();

print "<hr>\n";
print "<BR>";

print "<hr>\n";

print "<table width=100%><tr>\n";
print "<td>".$text{'gui_openvpn'}." <a href='javascript:window.open(\"https://openvpn.net/community-downloads/\")'>OPENVPN Clients</a></td>\n";
print "</tr></table>\n";

print "<hr>\n";
print "<BR>";

#footer della pagina
&footer("listvpn.cgi", $text{'list_server_vpn'});
