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

@fields = ('CA_NAME','CA_EXPIRE','KEY_SIZE','KEY_CONFIG','KEY_DIR','KEY_COUNTRY','KEY_PROVINCE','KEY_CITY','KEY_ORG','KEY_EMAIL');

# Controlli parametri form
$in{'CA_NAME'} = lc($in{'CA_NAME'});
if (($in{'CA_NAME'} !~ /^[a-zA-Z0-9_\-\.]{4,}$/) or ($in{'CA_NAME'} =~ /\.{2,}/) or ($in{'CA_NAME'} =~ /\.$/)){
    &error($text{'error_ca_name_1'}." $&");
}

if ($in{'KEY_CONFIG'} !~ /\S/) {
    &error($text{'error_key_config_1'});
} elsif (!-s $in{'KEY_CONFIG'}) {
    &error($text{'error_key_config_2'});
}

if ($in{'CA_EXPIRE'} =~ /\D/) {
    &error($text{'error_ca_expire'});
}

if ($in{'KEY_COUNTRY'} !~ /\S/) {
    &error($text{'error_key_country'});
}

if ($in{'KEY_PROVINCE'} !~ /\S/) {
    &error($text{'error_key_province'});
}

if ($in{'KEY_CITY'} !~ /\S/) {
    &error($text{'error_key_city'});
}

if ($in{'KEY_ORG'} !~ /\S/) {
    &error($text{'error_key_org'});
}

if ($in{'KEY_EMAIL'} !~ /\S/) {
    &error($text{'error_key_email_1'});
} elsif ($in{'KEY_EMAIL'} !~ /^\S+@\S+$/) {
    &error($text{'error_key_email_2'});
}

$in{'KEY_DIR'} = $config{'openvpn_home'}.'/'.$config{'openvpn_keys_subdir'};

if (-d $in{'KEY_DIR'}.'/'.$in{'CA_NAME'}) { &error($text{'error_ca_name_2'}); }

# intestazione pagina
&ui_print_header(undef, $text{'title_opnvpn'}, "", "intro", 1, 1, undef,
                &help_search_link("openvpn", "man", "doc", "google")."<a href=\"index.cgi\">".$text{'title_opnvpn'}."</a>",
                undef, undef, &text('index_openvpn')." ".&text('version')." ".$config{'openvpn_version'}.", ".&text('index_openssl')." ".&text('version')." ".$config{'openssl_version'});

&create_CA(\%in);

open CONFIG,">".$in{'KEY_DIR'}."/".$in{'CA_NAME'}."/ca.config";
print CONFIG "\$info_ca = {\n";
foreach $key (@fields) {
    if ($in{$key} =~ /'/) { $in{$key} =~ s/'/\\'/g; }; #'
    print CONFIG $key."=>'".$in{$key}."',\n";
}
print CONFIG "}\n";
close CONFIG;

print "<BR><BR>";

#footer della pagina
&footer("", $text{'title_opnvpn'});
