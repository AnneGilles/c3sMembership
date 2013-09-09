#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# you need python-gnupg, so
# bin/pip install python-gnupg

import gnupg
import tempfile
import shutil

DEBUG = False
#DEBUG = True


def encrypt_with_gnupg(data):
    """
    this function encrypts "data" with gnupg.

    returns strings:
    -----BEGIN PGP MESSAGE-----\nVersion: GnuPG v1.4.11 (GNU/Linux)\n
    ...
    -----END PGP MESSAGE-----\n
    """
    # we use a folder named 'keys' to store stuff

#    if os.path.exists("keys"):
#        if DEBUG:  # pragma: no cover
#            print("===================================== GNUPG START")
#            print "folder 'keys' exists"
        # shutil.rmtree("keys")     # delete to renew
        # print "deleted keys"

    # tempfile approach
    keyfolder = tempfile.mkdtemp()
#    print(keyfolder)
# TODO: check for a better way to do this:
# do we really need to create a new tempdir for every run? no!
# but hey as long as we need to run both as 'normal' user (while testing
# on port 6544) and as www-data (apache) we do need separate folders,
# because only the creator may access it.
# however: as long as this is reasonably fast, we can live with it. for now...

#    if DEBUG:  # pragma: no cover
#        # a gpg object to work with
#        gpg = gnupg.GPG(gnupghome="keys", verbose=True)
#    else:
        #gpg = gnupg.GPG(gnupghome="keys")
    gpg = gnupg.GPG(gnupghome=keyfolder)
    gpg.encoding = 'utf-8'

    # check if we have the membership key
    list_of_keys = gpg.list_keys()
    if DEBUG:  # pragma: no cover
        print("=== the list of keys: " + repr(list_of_keys))

    if not 'C3S-Yes!' in str(list_of_keys):
        # open and read key file
        # reading public key
#        pubkey_file = open('keys/C3S-Yes!.asc', 'r')
#        pubkey_content = pubkey_file.read()
#        pubkey_file.close()

        pubkey_content = """
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.11 (GNU/Linux)
Comment: GPGTools - http://gpgtools.org

mQENBFBIqlMBCADR7hxvDnwJkLgXU3Xol71eRkdNCAdIDnXQq/+Bmn5rxcJcXzNK
DyibSGbVVpwMMOIiVuKxM66QdlvBm+2/QUdD/kdcMTwRBFqP40N9T+vaIVDpit4r
6ZH1w8QD6EJTL0wbtmIkdAYMhYd0k4wDJ+xOcfx/VINiwhS5/DT38jimqmkaOEzs
DqzbBBogdZ+Tw+leC+D9JkSzGRjwO+UzUxjw4kdib9KbSppTbjv7HdL+Pn1y0ACd
2ELZjTumqQzQi19WFENNhMaRHlUU5iGp9sLbKUN0GtgxGYIs85QNXH/5/0Qr2ZjH
2/yZCyyWzZR0efut6WthcxFNb4OMDs056v5LABEBAAG0KUMzUyBZZXMhIChodHRw
Oi8vd3d3LmMzcy5jYykgPHllc0BjM3MuY2M+iQE+BBMBAgAoAhsDBgsJCAcDAgYV
CAIJCgsEFgIDAQIeAQIXgAUCUiq4KQUJA8GIDQAKCRBx9rqRzdKBECvrB/4unddV
mUfDHDShz+uIzz00OL642nNYi7vwfkpqGqMlooExQ9v365RhVKvTrDZwfzEh39pK
89BZumOI02QapIi0yDVPvwYMLeqm6lH8SuzMULC2gduyx2ZVB/meT/XjVyNzjS6c
RSbCJByfUjOg86JrOD/qTOiFfb3u678HEg8plAbw8/BmqayGBwyIZ0LMU97YJ8/+
vbGR876QpdVx82j+0Mj3P3LcI4ZFC6zrKX7lgcLlHCwxH1dg282TOoNhkrFwI9vE
Pp5ussW+XSikn5acaLdWNmM/xRxV5ghdGf6UVcKlRisWmSlsvnZFURAzojVo1wft
HKQd1hU9OuBHlU2fuQENBFBIqlMBCACoys54nxs3nrRcUkwFG0lp3L8N0udCzckI
iVgU/1SdgbfAD9rnRdKv4UE/uvn7MkfyO8V2V2OZANu8ZL+dtjmi6DWS2iTEXOl6
Mn6j0FyvZNDe6scvahPDjWYnrjOwrNy6FC5Y4eAyHTprABioZgfwNkonK5Oh0pXL
Rkr5z00lHjnkxYwyoFoMa3T7j7sxS0t3bkYZxETMCd+5YqDyt7fPEZ2sPugi1oqV
U/ytADNgEpjkzUhl4iWYYkk8RlQ8MFWVWEJd34HO6iOT+Pz6A9anuRbEqYCWYlHx
M3wBc2Klv/heN0yz5ldZVx1ug0/eLwexNecJOTpy2eQYjVLP/BwTABEBAAGJASUE
GAECAA8CGwwFAlIquGMFCQPBiA0ACgkQcfa6kc3SgRBbNAgAuIVSxLX/NkBONGCs
MNarw7n2K/Wz2HRiUBdIIpj3QESGwXmU/yGZOwxip/sAlG7G+AiqAM6dHgnqJ9Ho
6X6ieSCchUvekOdWaIV3yl+7jhoSwMh4LfbiMl2qoudqvaRE9wAcTZsD/ZPhr9Vh
E0tsJinMDVoyVCbQ860RAklp7KEvMLpZwtIJiEA2NbOit4j8JTfTJDra2S8c7SHD
s6XIhhv4NdtjsuLkiaRx7DLiCOTuRXUBFwb8x7vsqL3tX8jusmOSe/QnPjNWmUzZ
6NF/ZJ6zeecAd0wFSdQAHmlJfSB7L7VLKsLkuKhIgSeFP5xRht6AOpkS2DGPfrGb
VFtNoQ==
=85dz
-----END PGP PUBLIC KEY BLOCK-----
"""
# -----BEGIN PGP PUBLIC KEY BLOCK-----
# Version: GnuPG v1.4.11 (GNU/Linux)

# mQENBFBIqlMBCADR7hxvDnwJkLgXU3Xol71eRkdNCAdIDnXQq/+Bmn5rxcJcXzNK
# DyibSGbVVpwMMOIiVuKxM66QdlvBm+2/QUdD/kdcMTwRBFqP40N9T+vaIVDpit4r
# 6ZH1w8QD6EJTL0wbtmIkdAYMhYd0k4wDJ+xOcfx/VINiwhS5/DT38jimqmkaOEzs
# DqzbBBogdZ+Tw+leC+D9JkSzGRjwO+UzUxjw4kdib9KbSppTbjv7HdL+Pn1y0ACd
# 2ELZjTumqQzQi19WFENNhMaRHlUU5iGp9sLbKUN0GtgxGYIs85QNXH/5/0Qr2ZjH
# 2/yZCyyWzZR0efut6WthcxFNb4OMDs056v5LABEBAAG0KUMzUyBZZXMhIChodHRw
# Oi8vd3d3LmMzcy5jYykgPHllc0BjM3MuY2M+iQE+BBMBAgAoBQJQSKpTAhsDBQkB
# 4TOABgsJCAcDAgYVCAIJCgsEFgIDAQIeAQIXgAAKCRBx9rqRzdKBECXRCADA+HuD
# D6qoyMHBpsf8vuVyQfsORyuTfTe+Pv35WbsgPGtFpPmLXKaWbGRuCYl/FSOkd/ws
# VzucQNUhHmZGnmbtMv24+eyPPjbOGzG66DLSKcmL64Eaev23k7tCfpUK8pLB38ub
# FRoZ8PY2oSzkybQqRnqCN1rCRzXqOCsqXts+WqTmOR5s+o5VSisEtiaekBcPkV3H
# 3bGut6yIh9fwSw6RoKsjhdUgXz94wxS+3K8BDmo28rsfPuBcc0YqWk2Dm9jo3L9v
# fASXB277bE60RGJlBvOpM23ArxfbCaXEyq5GUtmaZLqgPy021QSikHeG0rreeA8x
# b7g+mAsuVH08eYnBuQENBFBIqlMBCACoys54nxs3nrRcUkwFG0lp3L8N0udCzckI
# iVgU/1SdgbfAD9rnRdKv4UE/uvn7MkfyO8V2V2OZANu8ZL+dtjmi6DWS2iTEXOl6
# Mn6j0FyvZNDe6scvahPDjWYnrjOwrNy6FC5Y4eAyHTprABioZgfwNkonK5Oh0pXL
# Rkr5z00lHjnkxYwyoFoMa3T7j7sxS0t3bkYZxETMCd+5YqDyt7fPEZ2sPugi1oqV
# U/ytADNgEpjkzUhl4iWYYkk8RlQ8MFWVWEJd34HO6iOT+Pz6A9anuRbEqYCWYlHx
# M3wBc2Klv/heN0yz5ldZVx1ug0/eLwexNecJOTpy2eQYjVLP/BwTABEBAAGJASUE
# GAECAA8FAlBIqlMCGwwFCQHhM4AACgkQcfa6kc3SgRBoPQgAx/73uYoQfqFrfCDd
# HRnzf2r3CyMOMYpmHmzVQjqsvVWUc59g1xpxG25CFYRTvC2OpJFP+yLsW52TbJjQ
# PYKdzV4zmjDJPb9msu4Bztrg+lZEpovqSF4Au9Jii7DbE1TQ8zItMzTGvC0deP4+
# SY27efmf3PHSXS4TIQxas5d+Y0sa3RyiE0E97uK7akJMDDS6l3t0YWaOfXhtknNV
# aGvLiYsbGr6JUEtnpCo0TawHtkxFy7L3bi9CF2dSF0oOzQWXh/LjLeiosh/oL7ce
# TN71vKWaPJFWl5pXxsEUGCdq2UUTRviHNx2+lzzdOmYBL+kaoHC5C50NuahZ4KAh
# BxTGRw==
# =ZhQb
# -----END PGP PUBLIC KEY BLOCK-----
# """
#
#
#
#         pubkey_content = """
# -----BEGIN PGP PUBLIC KEY BLOCK-----
# Version: GnuPG v1.4.12 (GNU/Linux)

# mQGiBDx8/iQRBADrEHpMDWZKVkXcezYpCllQ8BxR1nKoGvQ6MumnOiIr9Mnp68nm
# bGvF/g//de8j6YRoAVPKNVgFuvKxn0gpZE9TyhBconnmB77sFbME+G5MDOUjJCgp
# MqmtHmyYizJSi6KQZ0CPTnc485IZ15F52mwxTp6yMVkIgpnSKq4y0p8d1wCg5iss
# GFj3qFNqsiBWp0nCGbWhvMkEAJELizEX/Cgf+OtoagsmiFnU5F9h/8ofNsXDZijk
# T4Rrc/fLtf8EeZXBdAYuKkjMYO3fw/T4Q66rKRlR1qapoo1vlLFKEzVmyUfJ4R7h
# lWN55Ab7pvE/E5+Sa3As3AF8IuCtjqR6C4mnXd7cU0YIrMw5YmJUFGkBj8d1mE4h
# 45wvBADe3MfYdbMJlF2i8V1K1nB0t4fucm78cq1/VS+v4Ew5aQ9NW3f1+9g+IRBE
# xY9hgNqP0SRZwH/f4wGWVARnE5a+gD16X0U2OhpaweN9u+VOHuplLuAyDYb+Z+hw
# O/95B36QLKP49izusH5+70gNy17NZJLPgieJrMq/ILc5FZf607QkbWVpayBtaWNo
# YWxrZSA8bWVpay5taWNoYWxrZUBoaHUuZGU+iGIEExECACIFAk6V2AUCGwMGCwkI
# BwMCBhUIAgkKCwQWAgMBAh4BAheAAAoJEOg8fPx8tvkPhsMAoLBs+z8cdE8jSo0q
# pipJ9qFTrkA4AJ40ArpviVcSlYW0OYaeovK2c2tlQbQnbS5laWsgbWljaGFsa2Ug
# PG1Ab3Blbm11c2ljY29udGVzdC5vcmc+iGAEExECACAFAkWwvDgCGwMGCwkIBwMC
# BBUCCAMEFgIDAQIeAQIXgAAKCRDoPHz8fLb5DwalAKDat72JljEcjx6Z47Ww0EkH
# OYE1FQCfUesBCb8xOqAg3nxLKqj6YOp54Py0MW0uZWlrIG1pY2hhbGtlIDxtZWlr
# Lm1pY2hhbGtlQHVuaS1kdWVzc2VsZG9yZi5kZT6IYAQTEQIAIAUCROM4cwIbAwYL
# CQgHAwIEFQIIAwQWAgMBAh4BAheAAAoJEOg8fPx8tvkP1l8AnRBJqQItItTgMdzE
# 6M6we5XOVjqUAKCAzFzDbUJy3vem7L9BqX0yFaWJk7RIbWVpayBtaWNoYWxrZSAo
# aHR0cDovL3d3dy5sZWJlbnNsYWVuZ2xpY2gtdHJhdW1oYWZ0Lm9yZykgPG1AcmVh
# a3RhbnouZGU+iF4EExECAB4FAkEotIQCGwMGCwkIBwMCAxUCAwMWAgECHgECF4AA
# CgkQ6Dx8/Hy2+Q/PKQCfTzKaMg1YhPKjSdhycb2s9iiG6S0AnRhCdHv4c+cYfrYn
# VdB6vUG8/bDFtDBtLmVpayBtaWNoYWxrZSAod3d3LmFuZ3N0YWx0LmRlKSA8bUBy
# ZWFrdGFuei5kZT6IVwQTEQIAFwUCPHz+JAULBwoDBAMVAwIDFgIBAheAAAoJEOg8
# fPx8tvkPWwMAoMBe4wVvUTEWuZ2/OmE84Xp3M+MdAJ97FjzbKUwf80Lv5i06V1uY
# hvphH7REbS5laWsgbWljaGFsa2UgKGh0dHA6Ly9vcy5hc3RhLW1hcmJ1cmcuZGUp
# IDx0ZWNobmlrQGFzdGEtbWFyYnVyZy5kZT6IcAQwEQIAMAUCQdlKbykdIHdpbGwg
# YmUgc3RvcmVkIGluIGFuIGV4cGlyaW5nIGV4dHJhIGtleQAKCRDoPHz8fLb5DwoW
# AJ9cOKkabwWp3wc7nTG6tioZN4VmVQCgk4afDuUMrpQ0k56U8LF6Q12itLq0TW0u
# ZWlrIG1pY2hhbGtlIChodHRwOi8vd3d3LmFzdGEtbWFyYnVyZy5kZSkgPG9lZmZl
# bnRsaWNoa2VpdEBhc3RhLW1hcmJ1cmcuZGU+iHAEMBECADAFAkHZSjcpHSB3aWxs
# IGJlIHN0b3JlZCBpbiBhbiBleHBpcmluZyBleHRyYSBrZXkACgkQ6Dx8/Hy2+Q++
# 3QCgmpUDfrBdVAt4f2Sj0MB0gTxgumkAn0ad4LuEqkIes3B0+vqj3Q5t6aTFtDBt
# ZWlrIG1pY2hhbGtlIDxtZWlrLm1pY2hhbGtlQHVuaS1kdWVzc2VsZG9yZi5kZT6I
# YAQTEQIAIAUCRNdX6wIbAwYLCQgHAwIEFQIIAwQWAgMBAh4BAheAAAoJEOg8fPx8
# tvkPTMIAoN8d8nB+LcwRyrDMFbrmVGpFCOPrAKCiNRTcypSX/AreHbuTfUl3Fm3i
# jbQlbS5laWsgbWljaGFsa2UgPG1laWsubWljaGFsa2VAYzNzLmNjPohiBBMRAgAi
# BQJQT30SAhsDBgsJCAcDAgYVCAIJCgsEFgIDAQIeAQIXgAAKCRDoPHz8fLb5D0Gr
# AJ9caxHybrdd0yWIW8Ib1caZQKeJRgCfeKf0xrR8onaeaws9dI4SeO62Lyy5AQ0E
# PHz+JRAEAI7P1lBIpa5xaj5ngT2ceGNRwXLotTbX2o3jTjRD7o7eDqc5whgrSlhu
# azHGkTlE+9ic2n2SXSIvEr9nnEjAOV1bK16L1d1twEuY3S8KOTqOCgX0g8ekKIZq
# H3E8DVJAIVBRv8MSCR5Cx5HxRan0myOu9ifa+kfMGfJwV6gRuRxDAAMGA/9LxoR0
# mcMqE2t5Is4XOd1gLq9T8MDyOzRazKysXQpfz9KdFrS4qQQLrILTIElsTNa7z8bJ
# c/kjpSHBDyfX8xM07U1dVse0bhiA+5812+yWcT/9NM3/j8LnbTJBoLHtJSR929B4
# DmuJoLS3POPCfVaD4/CKw9c7SfgucNE4zvwy0YhFBBgRAgAGBQI8fP4lAAoJEOg8
# fPx8tvkPwwEAn37i0uLZkpmTSTpQZG6e5DCiqesAAJd9Y5WPSwCQfiYbtBYS3UON
# W+Ws
# =eoXN
# -----END PGP PUBLIC KEY BLOCK-----
# """

        # import public key
        gpg.import_keys(pubkey_content)
    else:
        if DEBUG:  # pragma: no cover
            print("=== not imported: key already known")
        pass

    if DEBUG:  # pragma: no cover
        print "list_keys(): " + str(gpg.list_keys())

    # prepare
    to_encode = data

    #if DEBUG:  # pragma: no cover
#    print("encrypt_with_gnupg: data: %s") % data
#    print("encrypt_with_gnupg: type(data): %s") % type(data)

#    print("type of to_encode: %s") % type(to_encode)
    if isinstance(to_encode, unicode):
        #print("type is unicode")
        to_encrypt = to_encode.encode(gpg.encoding)
    else:
        to_encrypt = to_encode
    #elif isinstance(to_encode, str):
    #    print("type was string")
    #    to_encrypt = to_encode.encode(gpg.encoding)
    #    print("type is now %s") % type(to_encrypt)
    #else:
    #    print("type is neither str nor unicode: %s") % type(to_encode)

    if DEBUG:  # pragma: no cover
        print "len(to_encrypt): " + str(len(str(to_encrypt)))
        # print("encrypt_with_gnupg: to_encrypt: %s") % to_encrypt
        print("encrypt_with_gnupg: type(to_encrypt): %s") % type(to_encrypt)

    # encrypt
    encrypted = gpg.encrypt(
        to_encrypt,
        '89FC70ECCAD4487972D8924D71F6BA91CDD28110',  # key fingerprint
        #'ED6CAAC657A45BCF55EAE6EFE83C7CFC7CB6F90F',  # key fingerprint
        always_trust=True)

    if DEBUG:  # pragma: no cover
        # print("encrypt_with_gnupg: encrypted: %s") % encrypted
        print("encrypt_with_gnupg: type(encrypted): %s") % type(encrypted)
        print(
            "encrypt_with_gnupg: type(encrypted.data): %s"
        ) % type(
            encrypted.data)
        # print "encrypted: " + str(encrypted)
        # print "len(encrypted): " + str(len(str(encrypted)))
        print ("========================================== GNUPG END")
    shutil.rmtree(keyfolder)

    return encrypted.data


if __name__ == '__main__':  # pragma: no coverage

    my_unicode_text = u"""
    --                                      --
    --  So here is some sample text.        --
    --  With umlauts: öäß        --
    --  I want this to be encrypted.        --
    --  And then maybe send it via email    --
    --                                      --
    """
    result = encrypt_with_gnupg(my_unicode_text)
    print result

    my_string = """
    --                                      --
    --  So here is some sample text.        --
    --  With out umlauts.                   --
    --  I want this to be encrypted.        --
    --  And then maybe send it via email    --
    --                                      --
    """
    result = encrypt_with_gnupg(my_string)
    print result
