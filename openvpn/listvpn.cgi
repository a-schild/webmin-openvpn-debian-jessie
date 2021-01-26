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

($listvpn,$list_static_vpn) = &ReadVPN();

$listca = &ReadCAtoList();

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

print "<BR>";

# start tabella
print "<table border width=100%>\n";
# title row
print "<tr $tb>";
    print "<td colspan=11 nowrap><b>".$text{'list_server_vpn'}.":</b></td>\n";
print "</tr>\n";

# th row
print "<tr $tb>";
if (keys %{$listvpn}) {
    print "<td width='40%' nowrap><b>".$text{'name'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_management'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_ca'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_protocol'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_port'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_local'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'logs'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'clientlist'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_status'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'remove'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'action'}."</b></td>\n";
} else {
    print "<td colspan=11 nowrap align=center><b>".$text{'list_vpn_empty'}."</b></td>\n";
}
print "</tr>\n";
# rows
foreach $key (sort keys %{$listvpn}) {
    print "<tr $cb>\n";
	if ($$listvpn{$key}{VPN_ACTION} == 1) {
	    print "<td nowrap><a href=\"modify_vpn.cgi?vpn=".$$listvpn{$key}{VPN_NAME}."\" title=\"".$text{'modifyvpn'}."\">".$$listvpn{$key}{VPN_NAME}."</a></td>\n";
	} else {
	    print "<td nowrap><a href=\"modify_vpn.cgi?vpn=".$$listvpn{$key}{VPN_NAME}."\" title=\"".$text{'modifyvpn'}."\"><SPAN STYLE=\"color:red\">".$$listvpn{$key}{VPN_NAME}."</span></a></td>\n";
	}
	if ($$listvpn{$key}{management}) {
	    print "<td nowrap><a href=\"listactiveconnect.cgi?vpn=".$$listvpn{$key}{VPN_NAME}."\" title=\"".$text{'view_listactiveconnect'}."\">".$$listvpn{$key}{management}."</a></td>\n";
	} else {
	    print "<td>&nbsp;</td>\n";
	}
	foreach $k (qw/CA_NAME proto port local/) {
	    if ($$listvpn{$key}{$k}) {
		print "<td nowrap>".$$listvpn{$key}{$k}."</td>\n";
	    } else {
		if ($k eq "local") {
		    print "<td>ALL</td>\n";
		} else {
		    print "<td>&nbsp;</td>\n";
		}
	    }
	}
	print "<td nowrap><a href=\"log_vpn.cgi?vpn=".$$listvpn{$key}{VPN_NAME}."\" title=\"".$text{'logvpn'}."\">".$text{'log'}."</a></td>\n";
	print "<td nowrap><a href=\"clientlist_vpn.cgi?vpn=".$$listvpn{$key}{VPN_NAME}."\" title=\"".$text{'clientlistvpn'}."\">".$text{'clientlist'}."</a></td>\n";
	# attivo
	if ($$listvpn{$key}{VPN_STATUS} == 1) {
	    print "<td nowrap><a href=\"action_vpn.cgi?action=disable&vpn=".$$listvpn{$key}{VPN_NAME}."\" title=\"".$text{'disablevpn'}."\">".$text{'disable'}."</a></td>\n";
	# inattivo
	} else {
	    print "<td nowrap><a href=\"action_vpn.cgi?action=enable&vpn=".$$listvpn{$key}{VPN_NAME}."\" title=\"".$text{'enablevpn'}."\">".$text{'enable'}."</a></td>\n";
	}
	if ($$listvpn{$key}{VPN_ACTION} == 0) {
	    print "<td nowrap><a href=\"remove_vpn.cgi?vpn=".$$listvpn{$key}{VPN_NAME}."\" title=\"".$text{'removevpn'}."\">".$text{'remove'}."</a></td>\n";
	} else {
	    print "<td>&nbsp;</td>\n";
	}
	# vpn attiva
	if ($$listvpn{$key}{VPN_ACTION} == 1) {
	    print "<td nowrap><a href=\"action_vpn.cgi?action=stop&vpn=".$$listvpn{$key}{VPN_NAME}."\" title=\"".$text{'stopvpn'}."\">".$text{'stop'}."</a></td>\n";
	# vpn non attiva
	} else {
	    if ($$listvpn{$key}{VPN_STATUS} == 0) {
		print "<td>&nbsp;</td>\n";
	    } else {
		print "<td nowrap><a href=\"action_vpn.cgi?action=start&vpn=".$$listvpn{$key}{VPN_NAME}."\" title=\"".$text{'startvpn'}."\"><SPAN STYLE=\"color:red\">".$text{'start'}."</span></a></td>\n";
	    }
	}
    print "</tr>\n";
}
# stop tabella
print "</table>\n";
print "<BR>";
print "<hr>\n";

if (@$listca) {
    print &ui_form_start("new_vpn.cgi");
    print "<b>".$text{'ca'}.':</b> '.&ui_select('ca', '', $listca).$text{'newvpn_server_titlemsg'};
    print &ui_form_end([ [ undef, $text{'newvpn_server_title'} ] ]);
} else {
    print &ui_buttons_start();
    print &ui_buttons_row("/openvpn/",$text{'newca_title'},$text{'newvpn_server_title_nocamsg'});
    print &ui_buttons_end();
}

print "<hr>\n";
print "<BR>";

# start tabella
print "<table border width=100%>\n";
# title row
print "<tr $tb>";
    print "<td colspan=10 nowrap><b>".$text{'list_static_server_vpn'}."</b></td>\n";
print "</tr>\n";

# th row
print "<tr $tb>";
if (keys %{$list_static_vpn}) {
    print "<td width='40%' nowrap><b>".$text{'name'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_management'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_protocol'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_port'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_ifconfig'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'logs'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_client'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'h_status'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'remove'}."</b></td>\n";
    print "<td width='1%' nowrap><b>".$text{'action'}."</b></td>\n";
} else {
    print "<td colspan=10 nowrap><b>".$text{'list_vpn_empty'}."</b></td>\n";
}
print "</tr>\n";
# rows
foreach $key (sort keys %{$list_static_vpn}) {
    print "<tr $cb>\n";
	if ($$list_static_vpn{$key}{VPN_ACTION} == 1) {
	    print "<td nowrap><a href=\"modify_static_vpn.cgi?vpn=".$$list_static_vpn{$key}{VPN_NAME}."\" title=\"".$text{'viewvpn'}."\">".$$list_static_vpn{$key}{VPN_NAME}."</a></td>\n";
	} else {
	    print "<td nowrap><a href=\"modify_static_vpn.cgi?vpn=".$$list_static_vpn{$key}{VPN_NAME}."\" title=\"".$text{'viewvpn'}."\"><SPAN STYLE=\"color:red\">".$$list_static_vpn{$key}{VPN_NAME}."</span></a></td>\n";
	}
	if ($$list_static_vpn{$key}{management}) {
	    print "<td nowrap><a href=\"listactiveconnect.cgi?static=1&vpn=".$$list_static_vpn{$key}{VPN_NAME}."\" title=\"".$text{'view_listactiveconnect'}."\">".$$list_static_vpn{$key}{management}."</a></td>\n";
	} else {
	    print "<td>&nbsp;</td>\n";
	}
	foreach $k (qw/proto port ifconfig/) {
	    if ($$list_static_vpn{$key}{$k}) {
		print "<td nowrap>".$$list_static_vpn{$key}{$k}."</td>\n";
	    } else {
		print "<td>&nbsp;</td>\n";
	    }
	}
	print "<td nowrap><a href=\"log_vpn.cgi?vpn=".$$list_static_vpn{$key}{VPN_NAME}."\" title=\"".$text{'logvpn'}."\">".$text{'log'}."</a></td>\n";
	print "<td nowrap><a href=\"export_client.cgi?vpn=".$$list_static_vpn{$key}{VPN_NAME}."\" title=\"".$text{'export_client'}."\">".$text{'export'}."</a></td>\n";
	# attivo
	if ($$list_static_vpn{$key}{VPN_STATUS} == 1) {
	    print "<td nowrap><a href=\"action_vpn.cgi?action=disable&vpn=".$$list_static_vpn{$key}{VPN_NAME}."\" title=\"".$text{'disablevpn'}."\">".$text{'disable'}."</a></td>\n";
	# inattivo
	} else {
	    print "<td nowrap><a href=\"action_vpn.cgi?action=enable&vpn=".$$list_static_vpn{$key}{VPN_NAME}."\" title=\"".$text{'enablevpn'}."\">".$text{'enable'}."</a></td>\n";
	}
	if ($$list_static_vpn{$key}{VPN_ACTION} == 0) {
	    print "<td nowrap><a href=\"remove_static_vpn.cgi?vpn=".$$list_static_vpn{$key}{VPN_NAME}."\" title=\"".$text{'removevpn'}."\">".$text{'remove'}."</a></td>\n";
	} else {
	    print "<td>&nbsp;</td>\n";
	}
	# vpn attiva
	if ($$list_static_vpn{$key}{VPN_ACTION} == 1) {
	    print "<td nowrap><a href=\"action_vpn.cgi?action=stop&vpn=".$$list_static_vpn{$key}{VPN_NAME}."\" title=\"".$text{'stopvpn'}."\">".$text{'stop'}."</a></td>\n";
	# vpn non attiva
	} else {
	    if ($$list_static_vpn{$key}{VPN_STATUS} == 0) {
		print "<td>&nbsp;</td>\n";
	    } else {
		print "<td nowrap><a href=\"action_vpn.cgi?action=start&vpn=".$$list_static_vpn{$key}{VPN_NAME}."\" title=\"".$text{'startvpn'}."\"><SPAN STYLE=\"color:red\">".$text{'start'}."</SPAN></a></td>\n";
	    }
	}
    print "</tr>\n";
}
# stop tabella
print "</table>\n";

print "<BR>";
print "<hr>\n";

print &ui_buttons_start();
print &ui_buttons_row("new_static_vpn.cgi",$text{'newvpn_static_server_title'},$text{'newvpn_static_servermsg'}." ".$in{'vpn'});
print &ui_buttons_end();

#print "<table width=100%><tr>\n";
#print "<form action=new_static_vpn.cgi>\n";
#print "<td><input type=submit value=\"$text{'newvpn_static_server_title'}\"></td>\n";
#print "<td>".$text{'newvpn_static_servermsg'}." ".$in{'vpn'}."</td>\n";
#print "</tr></form></table>\n";

print "<hr>\n";
print "<BR>";

#footer della pagina
&footer("", $text{'title_opnvpn'});
