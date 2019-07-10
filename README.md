=========================
Modulo: cq_mrp_repair_10
=========================

==========================================================
Enhancements for Odoo r.10 Community edition repair module
==========================================================

Sistemazioni modulo mrp_repair
==============================



AS Sprint 4 - Area Riparazioni
------------------------------

Sistemazioni al flusso di preventivo / esecuzione riparazione:
 - Flag "Magazzino Riparazioni" sul magazzino di default per le riparazioni, da attivare.
 - Metodo di fatturazione: impostato default a "Dopo la Riparazione".
 - I prodotti di tipo "Servizio" non generano movimenti di magazzino.
 - Data sul preventivo, modificabile solo in bozza (prende la data odierna come default).
 - Dopo l'avvenuta conferma del preventivo e a riparazione iniziata, l'utente può inserire dei prodotti/lavorazioni aggiuntivi a quelle preventivati nella tabella "Operazioni Aggiuntive".
   Se tali prodotti sono impostati da fatturare, il loro importo viene aggiunto al preventivo e il totale aggiornato.

Sistemazioni alla stampa del preventivo / ordine di riparazione (traduzioni, layout).
