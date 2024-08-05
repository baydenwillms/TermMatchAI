'''
You can use this repository: https://github.com/NOAA-Omics/noaa-omics-templates to get your lists of terms,
Or, Copy and Paste
'''

def get_term_lists():
	# Water_sample_data from Version 2 data template
	noaa_template_terms=['sample_name', 'sample_type', 'serial_number', 'cruise_id', 'line_id', 'station', 'locationID', 'habitat_natural_artificial_0_1', 
						'ctd_bottle_no', 'sample_replicate', 'source_material_id', 'biological_replicates', 'extract_number', 'sample_title', 'bioproject_accession', 
						'biosample_accession', 'notes_sampling', 'amplicon_sequenced', 'metagenome_sequenced', 'organism', 'verbatimEventDate', 'eventDate', 'minimumDepthInMeters', 
						'maximumDepthInMeters', 'env_broad_scale', 'env_local_scale', 'env_medium', 'geo_loc_name', 'waterBody', 'country', 'decimalLatitude', 'decimalLongitude', 'collection_method', 
						'samp_collect_device', 'samp_size', 'samp_size_unit', 'samp_vol_we_dna_ext', 'samp_vol_ext_unit', 'samp_mat_process',
						'filter_passive_active_0_1', 'filter_onsite_dur', 'size_frac', 'sterilise_method', 'samp_store_dur', 'samp_store_loc', 'samp_store_temp', 
						'samp_store_sol', 'description', 'date_modified', 'modified_by']

	# New (incoming) data template
	user_terms=['eventID', 'country', 'decimalLatitude', 'decimalLongitude', 'eventEnteredBy', 'locality', 'yearCollected', 'samplingProtocol', 'collectorList', 
				'continentOcean', 'county', 'dayCollected', 'depthOfBottomInMeters', 'habitat', 'horizontalDatum', 'island', 'islandGroup', 'landowner', 'maximumDepthInMeters', 
				'maximumElevationInMeters', 'coordinateUncertaintyInMeters', 'microHabitat', 'minimumDepthInMeters', 'minimumElevationInMeters', 'monthCollected', 'permitInformation', 
				'eventRemarks', 'stateProvince', 'taxTeam', 'timeOfDay', 'verbatimLatitude', 'verbatimLongitude', 'environmentalMedium', 'permitType', 'permitText', 'permitURI', 'permitStatus', 
				'recordedByID', 'bcid', 'expeditionCode', 'projectId']
	
	return(noaa_template_terms, user_terms)