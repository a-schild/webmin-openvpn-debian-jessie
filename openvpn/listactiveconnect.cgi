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

$vpns = {};
$vpnstatics = {};

if ($in{'vpn'}) {
    if ($in{'static'} == 1) {
	&ReadStaticVPNConf();
	$$vpnstatics{$in{'vpn'}} = \%in;	
	($$vpnstatics{$in{'vpn'}}{'list_connections'},$$vpnstatics{$in{'vpn'}}{'error_connections'}) = &ReadStaticConnections($in{'vpn'},$in{'management_url'},$in{'management_port'});
    } else { 
	&ReadVPNConf();
	$$vpns{$in{'vpn'}} = \%in;	
	($$vpns{$in{'vpn'}}{'list_connections'},$$vpns{$in{'vpn'}}{'error_connections'}) = &ReadConnections($in{'vpn'},$in{'management_url'},$in{'management_port'});
    }
} else {
    # solo quelle con management attivo
    ($vpns,$vpnstatics) = &ReadVPN(1);
    if (keys %{$vpns}) {
	foreach $vpn (keys %{$vpns}) {
    	    $$vpns{$vpn}{'management'} =~ /^(.+)\s+(\d+)$/;
	    $$vpns{$vpn}{'management_url'} = $1; $$vpns{$vpn}{'management_port'} = $2; 
	    ($$vpns{$vpn}{'list_connections'},$$vpns{$vpn}{'error_connections'}) = &ReadConnections($vpn,$$vpns{$vpn}{'management_url'},$$vpns{$vpn}{'management_port'});
	}
    }
    if (keys %{$vpnstatics}) {
	foreach $vpn (keys %{$vpnstatics}) {
	    $$vpnstatics{$vpn}{'management'} =~ /^(.+)\s+(\d+)$/;
	    $$vpnstatics{$vpn}{'management_url'} = $1; $$vpnstatics{$vpn}{'management_port'} = $2; 
	    ($$vpnstatics{$vpn}{'list_connections'},$$vpnstatics{$vpn}{'error_connections'}) = &ReadStaticConnections($vpn,$$vpnstatics{$vpn}{'management_url'},$$vpnstatics{$vpn}{'management_port'});
	}
    }
}

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

print "<BR>";

if (($in{'vpn'} and !$in{'static'}) or !$in{'vpn'}) {
    # start tabella
    print "<table border width=100%>\n";
    # title row
    print "<tr $tb>";
	print "<td colspan=7 nowrap><b>".$text{'listactiveconnect'}."</b></td>\n";
    print "</tr>\n";
    # th row
    print "<tr $tb>";
    if (keys %{$vpns}) {
	print "<td width='40%' nowrap><b>".$text{'name'}."</b></td>\n";
	print "<td width='1%' nowrap><b>".$text{'virtual_address'}."</b></td>\n";
        print "<td width='1%' nowrap><b>".$text{'bytes_received'}."</b></td>\n";
        print "<td width='1%' nowrap><b>".$text{'bytes_sent'}."</b></td>\n";
        print "<td width='1%' nowrap><b>".$text{'real_address'}."</b></td>\n";
        print "<td width='1%' nowrap><b>".$text{'connected_since'}."</b></td>\n";
        print "<td width='1%' nowrap><b>".$text{'key_remove'}."</b></td>\n";
    } else {
	print "<td colspan=7 align=center nowrap><b>".$text{'list_vpn_managed_empty'}."</b></td>\n";
    }
    print "</tr>\n";
    if (keys %{$vpns}) {
	# rows
        foreach $vpn (sort keys %{$vpns}) {
    	    print "<tr $tb>\n";
		print "<td colspan=7 nowrap><b>".$text{'server_vpn'}.': '.$vpn."</b></td>\n";
	    print "</tr>\n";
	    if (keys %{$$vpns{$vpn}{'list_connections'}}) {
		foreach $client (sort keys %{$$vpns{$vpn}{'list_connections'}}) {
		    print "<tr $cb>\n";
			print "<td nowrap>".$client."</td>\n";
			print "<td nowrap>".$$vpns{$vpn}{'list_connections'}{$client}{'virtual_address'}."</td>\n";
			print "<td nowrap>".$$vpns{$vpn}{'list_connections'}{$client}{'bytes_received'}."</td>\n";
			print "<td nowrap>".$$vpns{$vpn}{'list_connections'}{$client}{'bytes_sent'}."</td>\n";
			print "<td nowrap>".$$vpns{$vpn}{'list_connections'}{$client}{'real_address'}."</td>\n";
			print "<td nowrap>".$$vpns{$vpn}{'list_connections'}{$client}{'connected_since'}."</td>\n";
		        print "<td nowrap><a href=\"remove_client_connected.cgi?all=".$in{'all'}."&vpn=".$vpn."&client=".$client."\" title=\"".$text{'removeclientconnected'}."\">".$text{'stop_remove'}."</a></td>\n";
		    print "</tr>\n";
		}	
	    } elsif ($$vpns{$vpn}{'error_connections'}) {
		print "<tr $cb>\n";
		    print "<td colspan=7 nowrap><span bgcolor=red>".$text{'client_connected_failed'}." :".$$vpns{$vpn}{'error_connections'}."</span></td>\n";
		print "</tr>\n";
	    } else {
		print "<tr $cb>\n";
		    print "<td colspan=7 nowrap>".$text{'list_client_connected_empty'}."</td>\n";
		print "</tr>\n";
	    }
	}
    }
    # stop tabella
    print "</table>\n";

    print "<BR><BR>";
}

if (($in{'vpn'} and $in{'static'} == 1) or !$in{'vpn'}) {	
    # start tabella
    print "<table border width=100%>\n";
    # title row
    print "<tr $tb>";
	print "<td colspan=7 nowrap><b>".$text{'listactiveconnect_static'}."</b></td>\n";
    print "</tr>\n";
    # th row
    print "<tr $tb>";
    if (keys %{$vpnstatics}) {
	print "<td width='40%' nowrap><b>".$text{'name'}."</b></td>\n";
        print "<td width='1%' nowrap><b>".$text{'virtual_address'}."</b></td>\n";
        print "<td width='1%' nowrap><b>".$text{'bytes_received'}."</b></td>\n";
        print "<td width='1%' nowrap><b>".$text{'bytes_sent'}."</b></td>\n";
        print "<td width='1%' nowrap><b>".$text{'real_address'}."</b></td>\n";
        print "<td width='1%' nowrap><b>".$text{'connected_since'}."</b></td>\n";
        print "<td width='1%' nowrap><b>".$text{'key_remove'}."</b></td>\n";
    } else {
        print "<td colspan=7 align=center nowrap><b>".$text{'list_vpn_managed_empty'}."</b></td>\n";
    }
    print "</tr>\n";
    if (keys %{$vpnstatics}) {
	# rows
        foreach $vpn (sort keys %{$vpnstatics}) {
    	    print "<tr $tb>\n";
		print "<td colspan=7 nowrap><b>".$text{'server_vpn'}.': '.$vpn."</b></td>\n";
	    print "</tr>\n";
	    if (keys %{$$vpnstatics{$vpn}{'list_connections'}}) {
		foreach $client (sort keys %{$$vpnstatics{$vpn}{'list_connections'}}) {
		    print "<tr $cb>\n";
			print "<td nowrap>".$client."</td>\n";
			print "<td nowrap>".$$vpnstatics{$vpn}{'list_connections'}{$client}{'virtual_address'}."</td>\n";
			print "<td nowrap>".$$vpnstatics{$vpn}{'list_connections'}{$client}{'bytes_received'}."</td>\n";
			print "<td nowrap>".$$vpnstatics{$vpn}{'list_connections'}{$client}{'bytes_sent'}."</td>\n";
			print "<td nowrap>".$$vpnstatics{$vpn}{'list_connections'}{$client}{'real_address'}."</td>\n";
			print "<td nowrap>".$$vpnstatics{$vpn}{'list_connections'}{$client}{'connected_since'}."</td>\n";
			print "<td nowrap><a href=\"remove_client_connected.cgi?all=".$in{'all'}."&vpn=".$vpn."&client=".$client."\" title=\"".$text{'removeclientconnected'}."\">".$text{'stop_remove'}."</a></td>\n";
		    print "</tr>\n";
		}	
	    } elsif ($$vpnstatics{$vpn}{'error_connections'}) {
		print "<tr $cb>\n";
		    print "<td colspan=7 nowrap><span bgcolor=red>".$text{'client_connected_failed'}." :".$$vpnstatics{$vpn}{'error_connections'}."</span></td>\n";
		print "</tr>\n";
	    } else {
		print "<tr $cb>\n";
#		    print "<td colspan=7 nowrap>".$text{'list_client_connected_empty'}."</td>\n";
		    print "<td colspan=7 nowrap>".$text{'not_info'}."</td>\n";
		print "</tr>\n";
	    }
	}
    }
    # stop tabella
    print "</table>\n";

    print "<BR><BR>";

}

if ($in{'all'}) {
    #footer della pagina
    &footer("", $text{'title_opnvpn'});
} else {
    &footer("listvpn.cgi", $text{'listserver_title'});
}